from pydantic import BaseModel, Field
from typing import List, Optional


class StartInterviewRequest(BaseModel):
    role: str = Field(..., description="Օրինակ՝ Python Developer, Data Scientist")
    difficulty: str = Field(default="Junior", description="Junior, Mid, Senior")
    topic: str


class SubmitAnswerRequest(BaseModel):
    session_id: str
    question_text:str
    user_answer:str
    role:str
    difficulty:str
    topic:str
    question_id:int

class QuestionEvaluation(BaseModel):
    score: int = Field(..., ge=0, le=10, description="Score from 0 to 10 points")
    strengths: List[str] = Field(..., description="Strengths of the answer")
    missing_points: List[str] = Field(..., description="Points that are missing or incomplete")
    feedback: str = Field(..., description="Overall feedback")

class NextQuestionResponse(BaseModel):
    question_id: int
    question_text: str
    topic: str
    difficulty: str
    previous_evaluation: Optional[QuestionEvaluation] = None

class VisualizationReport(BaseModel):
    topic_scores_chart: str
    score_progression_chart: str
    difficulty_chart: str
    response_time_chart: str