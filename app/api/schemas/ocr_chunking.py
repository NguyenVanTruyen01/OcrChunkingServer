from typing import Any, Dict, List, Optional
from pydantic import BaseModel, HttpUrl, Field

class CallbackWebhooks(BaseModel):
    """URLs to be called back after processing is finished."""
    metadata: Optional[str] = Field(
        None, description="Webhook to update document metadata"
    )
    toc: Optional[str] = Field(
        None, description="Webhook to update table of contents"
    )
    section_content: Optional[str] = Field(
        None, description="Webhook to store each section/chunk content"
    )
    auth_header: Optional[str] = Field(
        None, description="Optional Authorization header to include when calling"
    )

class OCRChunkingRequest(BaseModel):
    document_id: str = Field(..., description="Document id")
    url: HttpUrl = Field(..., description="Public URL of the document (PDF, image, etc.)")
    extra_meta: Optional[Dict[str, Any]] = Field(
        default=None, description="Optional additional metadata"
    )
    webhooks: Optional[CallbackWebhooks] = Field(
        None, description="Callback URLs to notify after processing"
    )

class OCRChunk(BaseModel):
    content: str = Field(..., description="Text content of the chunk")
    metadata: Dict[str, Any] = Field(..., description="Associated metadata for the chunk")

class OCRChunkingResponse(BaseModel):
    document_id: str = Field(..., description="Document id")
    chunks: List[OCRChunk] = Field(
        ..., description="List of chunks after OCR and text splitting"
    )

class ChunkingRequest(BaseModel):
    document_id: str = Field(..., description="Document id")
    text: str = Field(
        ...,
        description="Plain text to split into overlapping chunks. Must be raw text only.",
    )
    base_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional metadata to attach to each resulting chunk",
    )

class ChunkingResponse(BaseModel):
    document_id: str = Field(..., description="Document id")
    chunks: List[OCRChunk] = Field(
        ..., description="List of text chunks with metadata after splitting"
    )