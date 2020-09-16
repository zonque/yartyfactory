from pydantic import BaseSettings, PostgresDsn, validator
from typing import Any, Dict, Optional, Union

class Settings(BaseSettings):
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # ADMIN_EMAIL: str
    # ADMIN_PASSWORD: str
    ADMIN_USERNAME: str = "admin"
    API_V1_STR: str = "/api/v1"
    POSTGRES_SERVER: str = ""
    POSTGRES_USER: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""
    PROJECT_NAME: str = "Software artifact feeder"
    PROJECT_DESCRIPTION: str = "API and database for software artifact feeding"
    STORAGE_S3_BUCKET: str = ""
    STORAGE_CDN_BASE_URL: str = ""
    SECRET_KEY: str
    SQLALCHEMY_DATABASE_URI: Union[Optional[PostgresDsn], Optional[str]] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
