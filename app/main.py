from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as api_router

# 1. Ստեղծում ենք FastAPI հավելվածի օբյեկտը
app = FastAPI(
    title="AI Mock Interview Platform",
    description="API for AI-powered mock technical interviews",
    version="1.0.0"
)

# 2. Ավելացնում ենք CORS Middleware (որպեսզի Frontend-ը կարողանա հարցումներ ուղարկել)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Թույլատրում ենք հարցումներ ցանկացած domain-ից
    allow_credentials=True,
    allow_methods=["*"],  # Թույլատրում ենք բոլոր HTTP մեթոդները (GET, POST, և այլն)
    allow_headers=["*"],  # Թույլատրում ենք բոլոր Header-ները
)

# 3. Միացնում ենք մեր API router-ը
app.include_router(api_router, prefix="/api")


@app.get("/")
def root():
    return {"message": "AI Mock Interview API is running!"}