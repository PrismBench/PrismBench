from functools import lru_cache

from pydantic import BaseModel, Field


class Settings(BaseModel):
    """
    Application settings loaded from environment or .env file.
    """

    REDIS_URL: str = Field("redis://redis:6379", env="REDIS_URL")
    AGENT_CONFIGS_PATH: str = Field("configs/agents", env="AGENT_CONFIGS_PATH")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached Settings instance.
    """
    return Settings()
