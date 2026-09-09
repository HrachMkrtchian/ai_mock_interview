import pandas as pd
from typing import List, Dict, Any
from app.services.visualization_service import VisualizationService

class AnalyticsService:
    def __init__(self):

        self.viz_service = VisualizationService()

    def calculate_session_analytics(self, responses_data: List[Dict[str, Any]]) -> Dict[str, Any]:

        if not responses_data:
            return {}


        df = pd.DataFrame(responses_data)

        
        overall_score = round(float(df['score'].mean()), 2)

        # 3. Score by topic (Միջին ըստ թեմաների)
        score_by_topic = df.groupby('topic')['score'].mean().round(2).to_dict()

        # 4. Strongest & Weakest topics
        topic_means = df.groupby('topic')['score'].mean()
        strongest_topic = str(topic_means.idxmax())
        weakest_topic = str(topic_means.idxmin())

        # 5. Success rate (Գոհացուցիչ/անցողիկ պատասխանների տոկոսը >= 7)
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
            series = df.groupby('topic')['score'].mean()
            return self.viz_service.generate_topic_scores_chart(series)

        elif chart_type == "progression":
            series = df.sort_values('question_index').set_index('question_index')['score']
            return self.viz_service.generate_score_progression_chart(series)

        elif chart_type == "difficulty":
            series = df.groupby('difficulty')['score'].mean()
            return self.viz_service.generate_difficulty_chart(series)

        elif chart_type == "response_time":
            series = df.groupby('topic')['time_taken_sec'].mean()
            return self.viz_service.generate_response_time_chart(series)

        raise ValueError(f"Unknown chart type: {chart_type}")
