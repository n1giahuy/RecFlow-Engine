from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    # Application settings
    app_name: str = Field("RecFlow Engine", validation_alias="APP_NAME")
    app_version: str = "1.0.0"

    environment: str = "prod"

    # Path settings
    faiss_index_path: str = "artifacts/faiss_index"
    metadata_path: str = "artifacts/enriched_books.parquet"

    # Model settings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    zero_shot_model: str = "facebook/bart-large-mnli"
    sentiment_model: str = "distilbert-base-uncased-finetuned-sst-2-english"

    # FAISS search settings
    faiss_candidate_count: int = 100
    default_top_k: int = 10

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )


settings = Settings()
