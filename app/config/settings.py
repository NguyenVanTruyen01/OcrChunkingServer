from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # --- Dev ---
    debug: bool = False

    # --- Azure Document Intelligence ---
    azure_di_endpoint: str
    azure_di_api_key: str | None = None
    azure_di_api_model: str = "prebuilt-layout"
    azure_di_mode: str = "markdown"
    azure_di_max_retries: int = 3

    # --- Chunking Service ---
    chunk_size: int = 1000
    chunk_overlap: int = 200
    chunk_separators: list[str] | None = None

settings = Settings()