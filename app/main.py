import sys
from pathlib import Path

# Նախագծի root (ai_mock_interview) թղթապանակը ավելացնում է Python path-ում
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from pathlib import Path
from dotenv import load_dotenv

# Նշում ենք .env ֆայլի ճշգրիտ ուղին app թղթապանակում
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path)
load_dotenv()
import os

from google import genai




# Ստանում է API Key-ը .env-ից
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as api_router
from google import genai

client = genai.Client()

interaction = client.interactions.create(
    model="gemini-3.8-flash",
    input="Explain how AI works in a few words"
)

print(interaction.output_text)
app = FastAPI(
    title="AI Mock Interview Platform",
    description="API for AI-powered mock technical interviews and analytics",
    version="1.0.0"
)

# CORS middleware Frontend-ի անխափան կապի համար
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/")
def root():
    return {"message": "AI Mock Interview API is running smoothly!"}


if __name__ == "__main__":
    import uvicorn
    # Այս տողը terminal-ում կտպի հղումը
    print("🚀 Server-ը աշխատում է: http://127.0.0.1:8000/docs")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)