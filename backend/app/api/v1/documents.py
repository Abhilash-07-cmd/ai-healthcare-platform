from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.schemas.document import DocumentResponse, DocumentListResponse, DocumentDetailResponse
from app.services.document_service import (
    upload_document,
    list_documents,
    get_document,
    delete_document
)
from app.api.deps import get_current_user
from app.models.all_models import User

router = APIRouter(prefix="/documents", tags=["Medical Document Management"])


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload Patient Medical Document",
    description=(
        "Upload a medical document (PDF, PNG, JPG, JPEG, DOCX — max 10MB). "
        "The document is saved securely, chunked into the RAG knowledge base pipeline, "
        "and indexed for future AI-context retrieval."
    )
)
async def upload_medical_document(
    file: UploadFile = File(..., description="Medical document file (PDF, PNG, JPG, DOCX)"),
    title: Optional[str] = Form(None, description="Document title (defaults to filename)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return upload_document(db=db, user=current_user, file=file, title=title or file.filename)


@router.get(
    "",
    response_model=DocumentListResponse,
    summary="List All Patient Documents",
    description="Returns all medical documents uploaded by the current user."
)
def list_my_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return list_documents(db=db, user=current_user)


@router.get(
    "/{document_id}",
    response_model=DocumentDetailResponse,
    summary="Get Document Details with Chunk Metadata",
    description="Returns full document details including RAG chunk metadata for the specified document."
)
def get_document_detail(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_document(db=db, user=current_user, doc_id=document_id)


@router.delete(
    "/{document_id}",
    summary="Delete Medical Document",
    description="Permanently deletes the document file from disk and all associated chunk metadata."
)
def delete_medical_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return delete_document(db=db, user=current_user, doc_id=document_id)
