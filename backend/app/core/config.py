from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    cors_origins: str = "http://localhost:3000"
    database_url: str = "sqlite:///./finsarthi.db"
    upload_dir: str = "./uploads"
    ocr_provider: str = "local"
    pinecone_api_key: str = ""
    pinecone_index: str = ""
    pinecone_environment: str = ""
    llm_api_key: str = ""
    llm_model: str = ""
    embedding_api_key: str = ""
    embedding_model: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def pinecone_enabled(self) -> bool:
        return bool(self.pinecone_api_key and self.pinecone_index)

    @property
    def llm_enabled(self) -> bool:
        return bool(self.llm_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()
