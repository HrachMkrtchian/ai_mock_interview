import os
from dotenv import load_dotenv

load_dotenv()


class Settings:

    OPENAI_API_KEY: str = os.getenv("GEMINI_API_KEY")

    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY-ը գտնված չէ .env ֆայլում:")

settings = Settings()