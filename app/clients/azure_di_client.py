from typing import List, Optional, Union, Iterable
from langchain_community.document_loaders.doc_intelligence import AzureAIDocumentIntelligenceLoader
from langchain_core.documents import Document
from app.config.settings import settings
from pathlib import Path

class AzureDIClient:
    """Wrapper for LangChain Azure Document Intelligence loader."""

    def __init__(self):
        pass

    def load(self, source: Union[str, bytes]) -> List[Document]:
        """Load a single file path/URL or bytes into LangChain Documents."""
        loader = self._make_loader(source)
        max_retries = settings.azure_di_max_retries
        for attempt in range(1, max_retries + 1):
            try:
                return loader.load()
            except Exception:
                if attempt == max_retries:
                    raise
        return []

    def load_many(self, sources: Iterable[Union[str, bytes]]) -> List[Document]:
        docs: List[Document] = []
        for s in sources:
            docs.extend(self.load(s))
        return docs

    def _make_loader(self, source: Union[str, bytes]) -> AzureAIDocumentIntelligenceLoader:
        cfg = dict(
            api_endpoint=settings.azure_di_endpoint,
            api_key=settings.azure_di_api_key,
            api_model=settings.azure_di_api_model,
            mode=settings.azure_di_mode,
        )
        if isinstance(source, bytes):
            cfg["bytes_source"] = source
        elif isinstance(source, str) and source.startswith(("http://", "https://")):
            cfg["url_path"] = source
        else:
            cfg["file_path"] = str(source)
        return AzureAIDocumentIntelligenceLoader(**cfg)
    

if __name__ == "__main__":
    # Initialize client
    client = AzureDIClient()

    # # Choose a local file or URL for testing
    # sample_path = Path("sample_2.pdf")

    # if not sample_path.exists():
    #     print("⚠️  sample.pdf not found. Provide a PDF path or URL to test.")
    # else:
    #     # Call the loader
    #     try:
    #         docs = client.load(sample_path)
    #         if docs:
    #             print("✅ Successfully parsed document.")
    #             print("Preview of first document page content:\n")
    #             print(docs[0].page_content)  # print first 500 chars
    #         else:
    #             print("No content returned.")
    #     except Exception as exc:
    #         print(f"❌ Error while loading document: {exc}")


    # URL to load
    url = "https://drive.eagleviet.com/s/Z67p6BHP8qX5ZrB/download/sample_2.pdf"

    try:
        docs = client.load(url)

        if docs:
            print("✅ Successfully parsed document from URL.")
            print("Number of pages / document chunks:", len(docs))
            print("Preview of first document chunk/page content:\n")
            print(docs[0].metadata)
        else:
            print("⚠️ No content returned from URL.")
    except Exception as exc:
        print(f"❌ Error while loading document from URL: {exc}")
