from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Response, HTTPException, status

from app.schemas.interview_schemas import (
    StartInterviewRequest,
    SubmitAnswerRequest,
    NextQuestionResponse,
    QuestionEvaluation
)
from app.services.llm_service import LLMService
from app.services.analytics_service import AnalyticsService

sessions_db: Dict[str, List[Dict[str, Any]]] = {}

router = APIRouter()
analytics_service = AnalyticsService()


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


@router.post("/submit-answer", response_model=QuestionEvaluation)
def submit_answer(
    request: SubmitAnswerRequest,
    llm_service: LLMService = Depends(get_llm_service)
):
    evaluation = llm_service.evaluate_answer(
        role=request.role,
        difficulty=request.difficulty,
        topic=request.topic,
        question_text=request.question_text,
        user_answer=request.user_answer
    )

    if request.session_id not in sessions_db:
        sessions_db[request.session_id] = []

    # Պահպանում ենք ընթացիկ պատասխանը
    sessions_db[request.session_id].append({
        "question_id": request.question_id,
        "topic": request.topic,
        "difficulty": request.difficulty,
        "score": evaluation.score
    })


    if len(sessions_db[request.session_id]) >= 4:
        final_summary = llm_service.calculate_final_result(sessions_db[request.session_id])

        sessions_db[f"{request.session_id}_result"] = final_summary

    return evaluation


@router.get("/final-result/{session_id}")
def get_final_result(session_id: str):
    result = sessions_db.get(f"{session_id}_result")
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Վերջնական արդյունքը չի գտնվել կամ հարցազրույցը դեռ ավարտված չէ:"
        )
    return result


@router.post("/analytics/session")
def calculate_analytics_from_body(responses: List[Dict[str, Any]]):
    return analytics_service.calculate_session_analytics(responses)


@router.get("/analytics/{session_id}")
def get_session_analytics(session_id: str):
    responses = sessions_db.get(session_id, [])

    if not responses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No answers found for this session"
        )

    return analytics_service.calculate_session_analytics(responses)


@router.get("/analytics/{session_id}/chart/{chart_type}")
async def get_session_chart(session_id: str, chart_type: str):
    responses_data = sessions_db.get(session_id, [])

    if not responses_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or has no data"
        )

    try:
        chart_bytes = analytics_service.get_chart_bytes(responses_data, chart_type)
        return Response(content=chart_bytes, media_type="image/png")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )