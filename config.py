import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "AI Mock Interview Platform"
    DEBUG: bool = True
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()