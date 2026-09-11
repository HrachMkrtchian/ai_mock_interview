import os
from google import genai
from google.genai import types
from app.schemas.interview_schemas import NextQuestionResponse, QuestionEvaluation


class LLMService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is missing")

        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.5-flash"

    def generate_question(self, role: str, difficulty: str, topic: str, question_id: int) -> NextQuestionResponse:
        prompt = f"""
        You are an expert technical interviewer.
        Generate question #{question_id} for a {difficulty} level {role} candidate.
        Topic: {topic}.
        Ensure you populate question_id as {question_id}, topic as '{topic}', and difficulty as '{difficulty}'.
        """

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=NextQuestionResponse,
            ),
        )

        result = NextQuestionResponse.model_validate_json(response.text)
        result.question_id = question_id
        result.topic = topic
        result.difficulty = difficulty
        return result

    def evaluate_answer(self, question_text: str, user_answer: str, role: str, difficulty: str, topic: str) -> QuestionEvaluation:
        prompt = f"""
        Evaluate the candidate's answer for the following question:
        Question: {question_text}
        User Answer: {user_answer}
        Candidate Role: {role}
        Question difficulty: {difficulty}
        Topic: {topic}
        Provide a evaluation with score (0 to 10), strengths, missing points, and overall feedback.
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