import os
import uuid
import math
import logging
from pathlib import Path
from typing import List

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session, joinedload

from app.models.all_models import Document, DocumentChunkMetadata, DocumentStatusEnum, User
from app.schemas.document import DocumentResponse, DocumentListResponse, DocumentDetailResponse

logger = logging.getLogger("healthcare_platform.document_service")

# ── Config ────────────────────────────────────────────────────────────────────
UPLOAD_BASE_DIR = Path(__file__).resolve().parent.parent.parent / "uploads" / "documents"
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".docx"}
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
CHUNK_SIZE_CHARS = 500  # Simulated RAG chunk size


def _get_user_upload_dir(user_id: int) -> Path:
    """Return per-user upload directory, creating it if needed."""
    user_dir = UPLOAD_BASE_DIR / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir


def _validate_file(file: UploadFile, content: bytes) -> None:
    """Validate file extension, content-type, and size."""
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{ext}' is not allowed. Accepted: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds the maximum allowed limit of 10 MB."
        )


def _simulate_rag_chunks(doc_id: int, content: bytes, file_type: str) -> List[DocumentChunkMetadata]:
    """
    Simulate the RAG chunking pipeline:
    - Splits raw content into fixed-size chunks.
    - Generates a mock Chroma vector ID for each chunk.
    - Stores chunk metadata in the DB (ready to plug in a real vector store).
    """
    # Decode bytes to text for preview (best-effort; skip for binary formats)
    try:
        text = content.decode("utf-8", errors="ignore")
    except Exception:
        text = f"[Binary content: {file_type}]"

    chunks = []
    total_chars = len(text)
    num_chunks = max(1, math.ceil(total_chars / CHUNK_SIZE_CHARS))

    for i in range(num_chunks):
        start = i * CHUNK_SIZE_CHARS
        chunk_text = text[start: start + CHUNK_SIZE_CHARS]
        chroma_id = f"doc_{doc_id}_chunk_{i}_{uuid.uuid4().hex[:8]}"
        chunks.append(
            DocumentChunkMetadata(
                document_id=doc_id,
                chunk_index=i,
                chroma_id=chroma_id,
                content_preview=chunk_text[:200] if chunk_text.strip() else None
            )
        )
    return chunks


def upload_document(
    db: Session,
    user: User,
    file: UploadFile,
    title: str
) -> DocumentResponse:
    # Read file into memory
    content = file.file.read()

    # Validate
    _validate_file(file, content)

    ext = Path(file.filename or "file").suffix.lower()
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    user_dir = _get_user_upload_dir(user.id)
    file_path = user_dir / unique_filename

    # Persist to disk
    with open(file_path, "wb") as f:
        f.write(content)

    # Create Document DB record
    doc = Document(
        title=title or file.filename or "Untitled Document",
        file_path=str(file_path),
        file_type=ext.lstrip(".").upper(),
        file_size=len(content),
        status=DocumentStatusEnum.PROCESSING,
        chunk_count=0,
        uploaded_by_user_id=user.id
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Simulate RAG chunking pipeline
    chunks = _simulate_rag_chunks(doc.id, content, doc.file_type)
    for chunk in chunks:
        db.add(chunk)

    # Mark as ready
    doc.status = DocumentStatusEnum.READY
    doc.chunk_count = len(chunks)
    db.commit()
    db.refresh(doc)

    logger.info(f"Document uploaded: id={doc.id}, title={doc.title}, chunks={doc.chunk_count}")
    return DocumentResponse.model_validate(doc)


def list_documents(db: Session, user: User) -> DocumentListResponse:
    docs = (
        db.query(Document)
        .filter(Document.uploaded_by_user_id == user.id)
        .order_by(Document.created_at.desc())
        .all()
    )
    return DocumentListResponse(
        total=len(docs),
        documents=[DocumentResponse.model_validate(d) for d in docs]
    )


def get_document(db: Session, user: User, doc_id: int) -> DocumentDetailResponse:
    doc = (
        db.query(Document)
        .options(joinedload(Document.chunks))
        .filter(
            Document.id == doc_id,
            Document.uploaded_by_user_id == user.id
        )
        .first()
    )
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )
    return DocumentDetailResponse.model_validate(doc)


def delete_document(db: Session, user: User, doc_id: int) -> dict:
    doc = db.query(Document).filter(
        Document.id == doc_id,
        Document.uploaded_by_user_id == user.id
    ).first()

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )

    # Remove file from disk
    try:
        if os.path.exists(doc.file_path):
            os.remove(doc.file_path)
    except OSError as e:
        logger.warning(f"Could not delete file {doc.file_path}: {e}")

    db.delete(doc)
    db.commit()
    return {"message": f"Document '{doc.title}' deleted successfully."}
