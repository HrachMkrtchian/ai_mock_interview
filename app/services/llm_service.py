import os
from google import genai
from google.genai import types
from app.schemas.interview_schemas import NextQuestionResponse, QuestionEvaluation


class LLMService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY value is missing")

        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-3.6-flash"

    def generate_question(self, role: str, difficulty: str, topic: str, question_id: int) -> NextQuestionResponse:
        prompt = f"""
        You are an expert technical interviewer.
        Generate question #{question_id} for a {difficulty} level {role} candidate.
        Topic: {topic}.
        Return ONLY the question text and topic.
        """

        # Gemini-ին փոխանցում ենք մեր Pydantic schema-ն՝ structured response ստանալու համար
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=NextQuestionResponse,
            ),
        )

        # Pydantic-ը ավտոմատ parse է անում JSON-ը
        result = NextQuestionResponse.model_validate_json(response.text)
        result.question_id = question_id
        return result

    def evaluate_answer(self, question_text: str, user_answer: str, role: str, difficulty: str , topic: str) -> QuestionEvaluation:
        prompt = f"""
        Evaluate the candidate's answer for the following question.
        Question: {question_text}
        User Answer: {user_answer}
        Candidate Role: {role}
        Question difficulty: {difficulty}
        Topic of the question: {topic}
        Provide a detailed evaluation with a score (0-10), strengths, missing points, and feedback.
        """

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=QuestionEvaluation,
            ),
        )

        return QuestionEvaluation.model_validate_json(response.text)