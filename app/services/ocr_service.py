from pathlib import Path
from typing import List, Union
from datetime import datetime, timezone
from urllib.parse import urlparse
import hashlib
import re
import requests

from langchain_core.documents import Document
from app.clients.azure_di_client import AzureDIClient


class OCRService:

    def __init__(self) -> None:
        self.client = AzureDIClient()

    def process(
        self,
        source: Union[str, bytes],
        extra_meta: dict | None = None  ,
    ) -> List[Document]:
        
        # Process
        docs = self.client.load(source)

        # Remove markers
        docs = self._remove_markers(docs)

        if not docs:
            return []

        base_meta = self._build_base_metadata(source, docs, extra_meta)
        enriched = [
            Document(
                page_content=d.page_content,
                metadata={**base_meta, "page_number": i + 1},
            )
            for i, d in enumerate(docs)
        ]
        return enriched

    def _build_base_metadata(
        self,
        source: Union[str, bytes],
        docs: List[Document],
        extra_meta: dict | None,
    ) -> dict:
        filename = self._guess_file_name(source)
        checksum = self._compute_checksum(source)
        page_count = len(docs)

        # Determine type and record original source if applicable
        if isinstance(source, str) and source.startswith(("http://", "https://")):
            source_type = "url"
            source_value = source                # remote URL
        elif isinstance(source, str):
            source_type = "file"
            source_value = str(Path(source))     # absolute/local path
        else:
            source_type = "bytes"
            source_value = None

        meta = {
            "file_name": filename,
            "page_count": page_count,
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "checksum_sha256": checksum,
            "source_type": source_type,
            "source": source_value
        }

        if extra_meta:
            meta.update(extra_meta)

        return meta

    @staticmethod
    def _guess_file_name(source: Union[str, bytes]) -> str:
        if isinstance(source, bytes):
            return "uploaded_bytes"
        if source.startswith(("http://", "https://")):
            return Path(urlparse(source).path).name or "downloaded_file"
        return Path(source).name

    @staticmethod
    def _compute_checksum(source: Union[str, bytes]) -> str | None:
        h = hashlib.sha256()

        if isinstance(source, bytes):
            h.update(source)
            return h.hexdigest()

        # Remote URL
        if isinstance(source, str) and source.startswith(("http://", "https://")):
            with requests.get(source, stream=True) as r:
                r.raise_for_status()
                for chunk in r.iter_content(chunk_size=8192):
                    h.update(chunk)
            return h.hexdigest()

        # Local file
        p = Path(source)
        if p.exists():
            with p.open("rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    h.update(chunk)
            return h.hexdigest()
        
        return None

    def _remove_markers(self, docs: List[Document]) -> List[Document]:
        cleaned: List[Document] = []
        pattern = re.compile(r'<!--\s*PageNumber="[^"]*"\s*-->')

        for d in docs:
            text = pattern.sub("", d.page_content).strip()
            # Keep the doc only if something remains
            if text:
                d.page_content = text
                cleaned.append(d)

        return cleaned

ocr_service = OCRService()