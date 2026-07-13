from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_base_url: str = ""
    hf_token: str = ""
    postgres_user: str = "transcript"
    postgres_password: str = "transcript"
    postgres_db: str = "transcript"
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    redis_url: str = "redis://redis:6379/0"
    whisperx_model: str = "large-v3"
    whisperx_device: str = "cuda"
    whisperx_compute_type: str = "float16"
    speaker_match_threshold: float = 0.82
    max_upload_mb: int = 4096
    max_record_sec: int = 3600
    cors_origins: str = "http://localhost:6004"
    uploads_dir: str = "/data/uploads"
    exports_dir: str = "/data/exports"
    text_embedding_dim: int = 768
    speaker_embedding_dim: int = 192
    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
settings = Settings()
