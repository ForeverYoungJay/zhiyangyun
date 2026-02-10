from pydantic import BaseModel
import os


class Settings(BaseModel):
    app_name: str = "SmartCare Backend"
    env: str = os.getenv("APP_ENV", "dev")
    db_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://smartcare:smartcare@localhost:5432/smartcare",
    )
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")


settings = Settings()
