from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator


class Settings(BaseSettings):
    APP_NAME: str = "Skills Assessment API"
    ENV: str = "dev"
    SECRET_KEY: str = "change_this_in_production"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    TEMP_TOKEN_EXPIRE_MINUTES: int = 5

    POSTGRES_HOST: str = "127.0.0.1"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "chatbot"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "1234"

    DATABASE_URL: str | None = None

    REDIS_URL: str = "redis://127.0.0.1:6379/0"

    # -------------------------
    # 🔥 TELEGRAM CONFIG
    # -------------------------
    TELEGRAM_BOT_TOKEN: str = ""  # REQUIRED
    TELEGRAM_WEBHOOK_SECRET: str = ""  # optional (for production security)

    FRONTEND_URL: str = "http://localhost:5173"

    PUBLIC_BASE_URL: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    @model_validator(mode="after")
    def _build_database_url(self):
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        return self


settings = Settings()