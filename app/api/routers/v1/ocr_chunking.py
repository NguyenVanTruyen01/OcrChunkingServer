from fastapi import APIRouter, HTTPException, Request
from app.api.schemas.ocr_chunking import (
    OCRChunkingRequest,
    OCRChunkingResponse,
    OCRChunk,
    ChunkingRequest,
    ChunkingResponse,
)
from app.services.ocr_service import ocr_service
from app.services.chunking_service import chunk_service
from typing import Dict, Any
import asyncio
from app.utils.webhook_client import send_webhook


router = APIRouter()


@router.get("/health-check")
async def health_check() -> str:
    return "healthy"


@router.post("/ocr")
async def ocr_only(payload: OCRChunkingRequest) -> OCRChunkingResponse:
    try:
        docs = ocr_service.process(source=str(payload.url), extra_meta=payload.extra_meta or {})
        if not docs:
            raise HTTPException(status_code=400, detail="No text extracted from the document.")

        # Treat the entire OCR text as one chunk
        chunk_items = [
            OCRChunk(content=d.page_content, metadata=d.metadata) for d in docs
        ]
        return OCRChunkingResponse( document_id=payload.document_id, chunks=chunk_items )

    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"OCR failed: {exc}")


@router.post("/chunking", response_model=ChunkingResponse)  
async def chunk_text(payload: ChunkingRequest) -> ChunkingResponse:
    try:
        chunks = chunk_service.split_text(
            text=payload.text,
            base_metadata=payload.base_metadata or {"source": "input_text"},
        )
        
        chunk_items = [OCRChunk(content=c.page_content, metadata=c.metadata) for c in chunks]
        return ChunkingResponse(document_id=payload.document_id, chunks=chunk_items  )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Chunking failed: {exc}")


@router.post("/ocr-chunking", response_model=OCRChunkingResponse)
async def ocr_and_chunking(payload: OCRChunkingRequest) -> OCRChunkingResponse:
    """
    Perform OCR on a remote document and split the extracted text into chunks.
    1. Downloads and extracts text from the document using Azure Document Intelligence.
    2. Splits the extracted text into overlapping chunks for downstream processing.
    """
    try:
        # Step 1: OCR to obtain a list of LangChain Document objects with metadata
        docs = ocr_service.process(source=str(payload.url), extra_meta=payload.extra_meta or {})
        if not docs:
            raise HTTPException(status_code=400, detail="No text extracted from the document.")

        # Step 2: Chunking the documents
        chunks = chunk_service.split_documents(docs)

        # Step 3: Convert to schema-friendly objects
        chunk_items = [
            OCRChunk(content=c.page_content, metadata=c.metadata) for c in chunks
        ]

        print( payload.document_id )

        # Fire callbacks asynchronously if provided
        if payload.webhooks:
            meta = chunk_items[0].metadata if chunk_items else {}
            if payload.webhooks.metadata:
                asyncio.create_task(send_webhook(payload.webhooks.metadata, {"metadata": meta}, payload.webhooks.auth_header))
            if payload.webhooks.toc:
                asyncio.create_task(send_webhook(payload.webhooks.toc, {"toc": []}, payload.webhooks.auth_header))
            if payload.webhooks.section_content:
                items = [
                    {"section_id": c.metadata.get("chunk_id"), "content": c.page_content, "metadata": c.metadata}
                    for c in chunks
                ]
                asyncio.create_task(send_webhook(payload.webhooks.section_content, {"sections": items}, payload.webhooks.auth_header))

        return OCRChunkingResponse( document_id=payload.document_id, chunks=chunk_items )

    except Exception as exc:
        # Any unexpected error will be returned as a 500 response
        raise HTTPException(status_code=500, detail=f"OCR/Chunking failed: {exc}")
    

@router.post("/metadata")
async def receive_metadata(request: Request) -> Dict[str, Any]:
    data = await request.json()
    print("[Webhook] Metadata received:", data)
    return {"status": "ok", "received": data}


@router.post("/toc")
async def receive_toc(request: Request) -> Dict[str, Any]:
    data = await request.json()
    print("[Webhook] TOC received:", data)
    return {"status": "ok", "received": data}


@router.post("/section-content")
async def receive_section_content(request: Request) -> Dict[str, Any]:
    data = await request.json()
    print("[Webhook] Section content received:", data)
    return {"status": "ok", "received": data}