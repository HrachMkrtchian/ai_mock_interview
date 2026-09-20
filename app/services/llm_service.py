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
        self.model_name = "gemini-3.1-flash-lite"

    def generate_question(self, role: str, difficulty: str, topic: str, question_id: int, lang: str = "AM") -> NextQuestionResponse:

        lang_map = {
            "AM": "Armenian",
            "RU": "Russian",
            "EN": "English"
        }
        lang_name = lang_map.get(lang, "Armenian")

        prompt = f"""
        You are an expert technical interviewer.
        Generate question #{question_id} for a {difficulty} level {role} candidate.
        Topic: {topic}.
        IMPORTANT: The generated question text must be strictly in {lang_name} language.
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
        Provide a evaluation with score (0 to 100), strengths, missing points, and overall feedback.
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


    def determine_next_difficulty(self, current_difficulty: str, score: float) -> str:

        levels = ["Junior", "Mid", "Senior", "Lead"]
        current_idx = levels.index(current_difficulty) if current_difficulty in levels else 0


        if score >= 80 and current_idx < len(levels) - 1:
            return levels[current_idx + 1]

        elif score <= 30 and current_idx > 0:
            return levels[current_idx - 1]

        return current_difficulty

    def calculate_final_result(self, history_evaluations: list[dict]) -> dict:

        DIFFICULTY_MAX_POINTS = {
            "Junior": 10,
            "Mid": 20,
            "Senior": 30,
            "Lead": 40
        }

        user_total_points = 0.0
        max_possible_points = 0.0

        for item in history_evaluations:
            diff = item.get("difficulty", "Junior")
            score = item.get("score", 0.0)

            question_max_points = DIFFICULTY_MAX_POINTS.get(diff, 100)


            user_total_points += (score / 100.0) * question_max_points

            max_possible_points += question_max_points


        final_percentage = (user_total_points / max_possible_points * 100) if max_possible_points > 0 else 0.0
        final_percentage = round(final_percentage, 1)

        is_passed = final_percentage >= 75.0

        return {
            "final_percentage": final_percentage,
            "is_passed": is_passed,
            "status": "PASSED" if is_passed else "FAILED",
            "total_earned_points": user_total_points,
            "total_possible_points": max_possible_points
        }