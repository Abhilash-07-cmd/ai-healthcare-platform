from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional


class DocumentResponse(BaseModel):
    id: int
    title: str
    file_type: str
    file_size: int
    status: str
    chunk_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentChunkResponse(BaseModel):
    id: int
    chunk_index: int
    chroma_id: str
    content_preview: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DocumentDetailResponse(BaseModel):
    id: int
    title: str
    file_type: str
    file_size: int
    status: str
    chunk_count: int
    created_at: datetime
    updated_at: datetime
    chunks: List[DocumentChunkResponse] = []

    model_config = ConfigDict(from_attributes=True)


class DocumentListResponse(BaseModel):
    total: int
    documents: List[DocumentResponse]
