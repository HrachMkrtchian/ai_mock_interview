from pydantic import BaseModel, Field
from typing import List, Optional, Union


class StartInterviewRequest(BaseModel):
    role: str = Field(..., description="Օրինակ՝ Python Developer, Data Scientist")
    difficulty: str = Field(default="Junior", description="Junior, Mid, Senior")
    topic: str = Field(..., description="Հարցազրույցի թեման")


class SubmitAnswerRequest(BaseModel):
    session_id: str
    question_text: str
    user_answer: str
    role: str
    difficulty: str
    topic: str
    question_id: int


class QuestionEvaluation(BaseModel):
    score: int = Field(..., description="Score from 0 to 10")
    strengths: List[str] = Field(default_factory=list, description="Strengths of the answer")
    missing_points: List[str] = Field(default_factory=list, description="Missing points")
    feedback: str = Field(..., description="Overall feedback")

class NextQuestionResponse(BaseModel):
    question_id: int
    question_text: str
    topic: str
    difficulty: str
    previous_evaluation: Optional[QuestionEvaluation] = None


