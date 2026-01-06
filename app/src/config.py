from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, PostgresDsn, PositiveInt
from sqlalchemy import URL

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    class DatabaseConfig(BaseModel):
        driver: PostgresDsn = "postgresql+asyncpg"
        host: str = "127.0.0.1"
        port: PositiveInt = 5432
        name: str
        user: str
        password: str

        @property
        def url(self) -> URL:
            return URL.create(
                host=self.host,
                port=self.port,
                database=self.name,
                username=self.user,
                password=self.password,
                drivername=str(self.driver),
            )

    db: DatabaseConfig

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_nested_delimiter="__",
        env_file=[BASE_DIR / ".env.example", BASE_DIR / ".env"],
        extra="ignore",
    )


settings = Settings()
