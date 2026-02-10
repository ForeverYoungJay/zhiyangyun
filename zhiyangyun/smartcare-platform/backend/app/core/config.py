import os
from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "SmartCare Backend"
    env: str = os.getenv("APP_ENV", "dev")
    db_url: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://smartcare:smartcare@localhost:5432/smartcare")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    jwt_secret: str = os.getenv("JWT_SECRET", "smartcare-dev-secret")
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = int(os.getenv("JWT_EXPIRE_MINUTES", "720"))


settings = Settings()
