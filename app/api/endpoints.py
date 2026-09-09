from fastapi import APIRouter, Depends , Response
from typing import Dict, Any, List
from app.schemas.interview_schemas import (
    StartInterviewRequest,
    SubmitAnswerRequest,
    NextQuestionResponse,
    QuestionEvaluation
)
from app.services.llm_service import LLMService
from app.services.analytics_service import AnalyticsService

sessions_db = {}

router = APIRouter()

analytics_service = AnalyticsService()


# Dependency Injection - ստեղծում է LLMService-ի օբյեկտը
def get_llm_service() -> LLMService:
    return LLMService()


@router.post("/start-interview", response_model=NextQuestionResponse)
def start_interview(
    request: StartInterviewRequest,
    llm_service: LLMService = Depends(get_llm_service)
):
    return llm_service.generate_question(
        role=request.role,
        difficulty=request.difficulty,
        topic=request.topic,
        question_id=1
    )

@router.post("/api/submit-answer")
def submit_answer(
    request: SubmitAnswerRequest,
    llm_service: LLMService = Depends()
):
    # 1. AI-ն գնահատում է պատասխանը
    evaluation = llm_service.evaluate_answer(
        role=request.role,
        difficulty=request.difficulty,
        topic=request.topic,
        question_text=request.question_text,
        user_answer=request.user_answer
    )


    if request.session_id not in sessions_db:
        sessions_db[request.session_id] = []

    # 3. Ավելացնում ենք ընթացիկ պատասխանը sessions_db-ում
    sessions_db[request.session_id].append({
        "question_id": request.question_id,
        "topic": request.topic,
        "difficulty": request.difficulty,
        "score": evaluation.score
    })

    # 4. Վերադարձնում ենք գնահատականը
    return evaluation

@router.post("/api/analytics/session")
def calculate_analytics_from_body(responses: List[Dict[str, Any]]):
    analytics = AnalyticsService.calculate_session_analytics(responses)
    return analytics

@router.get("/api/analytics/{session_id}")
def get_session_analytics(session_id: str):
    # 1. sessions_db-ից կարդում ենք տվյալ session_id-ի պատասխանների list-ը
    responses = sessions_db.get(session_id, [])

    # 2. Եթե պատասխաններ չկան, վերադարձնում ենք հաղորդագրություն
    if not responses:
        return {"message": "No answers found for this session"}

    # 3. Տվյալները փոխանցում ենք Pandas-ին
    analytics = AnalyticsService.calculate_session_analytics(responses)

    return analytics


@router.get("/analytics/{session_id}/chart/{chart_type}")
async def get_session_chart(session_id: str, chart_type: str):
    responses_data = sessions_db.get(session_id, [])

    if not responses_data:
        return Response(status_code=404)

    chart_bytes = analytics_service.get_chart_bytes(responses_data, chart_type)

    return Response(content=chart_bytes, media_type="image/png")