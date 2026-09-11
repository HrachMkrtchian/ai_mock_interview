import pandas as pd
from typing import List, Dict, Any
from app.services.visualization_service import VisualizationService


class AnalyticsService:
    def __init__(self):
        self.viz_service = VisualizationService()

    def calculate_session_analytics(self, responses_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not responses_data:
            return {
                "overall_score": 0.0,
                "total_questions": 0,
                "topics_evaluated": 0,
                "score_by_topic": {},
                "strongest_topic": None,
                "weakest_topic": None,
                "success_rate_percentage": 0.0,
            }

        df = pd.DataFrame(responses_data)

        if 'score' not in df.columns or df['score'].dropna().empty:
            return {
                "overall_score": 0.0,
                "total_questions": len(df),
                "topics_evaluated": 0,
                "score_by_topic": {},
                "strongest_topic": None,
                "weakest_topic": None,
                "success_rate_percentage": 0.0,
            }

        overall_score = round(float(df['score'].mean()), 2)

        if 'topic' in df.columns:
            score_by_topic = df.groupby('topic')['score'].mean().round(2).to_dict()
            topic_means = df.groupby('topic')['score'].mean()
            strongest_topic = str(topic_means.idxmax()) if not topic_means.empty else None
            weakest_topic = str(topic_means.idxmin()) if not topic_means.empty else None
        else:
            score_by_topic = {}
            strongest_topic = None
            weakest_topic = None

        passed_questions = df[df['score'] >= 7]
        success_rate = round(float((len(passed_questions) / len(df)) * 100), 2)

        return {
            "overall_score": overall_score,
            "total_questions": len(df),
            "topics_evaluated": len(score_by_topic),
            "score_by_topic": score_by_topic,
            "strongest_topic": strongest_topic,
            "weakest_topic": weakest_topic,
            "success_rate_percentage": success_rate,
        }

    def get_chart_bytes(self, responses_data: List[Dict[str, Any]], chart_type: str) -> bytes:
        if not responses_data:
            return b""

        df = pd.DataFrame(responses_data)

        if chart_type == "topic_scores":
            if 'topic' not in df.columns or 'score' not in df.columns:
                return b""
            series = df.groupby('topic')['score'].mean()
            return self.viz_service.generate_topic_scores_chart(series)

        elif chart_type == "progression":
            order_col = 'question_id' if 'question_id' in df.columns else ('question_index' if 'question_index' in df.columns else None)
            if not order_col or 'score' not in df.columns:
                return b""
            series = df.sort_values(order_col).set_index(order_col)['score']
            return self.viz_service.generate_score_progression_chart(series)

        elif chart_type == "difficulty":
            if 'difficulty' not in df.columns or 'score' not in df.columns:
                return b""
            series = df.groupby('difficulty')['score'].mean()
            return self.viz_service.generate_difficulty_chart(series)

        elif chart_type == "response_time":
            if 'topic' not in df.columns or 'time_taken_sec' not in df.columns:
                return b""
            series = df.groupby('topic')['time_taken_sec'].mean()
            return self.viz_service.generate_response_time_chart(series)

        raise ValueError(f"Unknown chart type: {chart_type}")