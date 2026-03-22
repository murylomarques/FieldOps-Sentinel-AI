from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "FIELDOPS SENTINEL AI"
    api_v1_prefix: str = "/api/v1"
    environment: str = "development"

    postgres_user: str = "fieldops"
    postgres_password: str = "fieldops123"
    postgres_db: str = "fieldops"
    postgres_port: int = 5432
    postgres_host: str = "localhost"
    database_url: str | None = None

    secret_key: str = "change-me"
    jwt_expire_minutes: int = 120
    algorithm: str = "HS256"

    cors_origins: str = "http://localhost:3000"
    rate_limit_per_minute: int = 120

    model_delay_path: str = "ml/models/delay_model.pkl"
    model_noshow_path: str = "ml/models/noshow_model.pkl"
    model_reschedule_path: str = "ml/models/reschedule_model.pkl"
    model_sla_path: str = "ml/models/sla_breach_model.pkl"
    feature_columns_path: str = "ml/models/feature_columns.json"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @field_validator("cors_origins")
    @classmethod
    def validate_cors(cls, value: str) -> str:
        return value.strip()


@lru_cache
def get_settings() -> Settings:
    return Settings()
