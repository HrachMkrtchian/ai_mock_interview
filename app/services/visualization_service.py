import io
import matplotlib
matplotlib.use('Agg')  # Headless mode backend-ի համար
import matplotlib.pyplot as plt
import pandas as pd


class VisualizationService:

    @staticmethod
    def _fig_to_bytes(fig) -> bytes:
        """Matplotlib figure-ն վերածում է հում PNG bytes-երի:"""
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf.getvalue()

    def generate_topic_scores_chart(self, topic_series: pd.Series) -> bytes:
        fig, ax = plt.subplots(figsize=(6, 4))
        topic_series.plot(kind='bar', ax=ax, color='skyblue', edgecolor='black')
        ax.set_title('Average Score by Topic')
        ax.set_xlabel('Topics')
        ax.set_ylabel('Average Score')
        ax.set_ylim(0, 10)
        plt.xticks(rotation=45)
        return self._fig_to_bytes(fig)

    def generate_score_progression_chart(self, progression_series: pd.Series) -> bytes:
        fig, ax = plt.subplots(figsize=(6, 4))
        progression_series.plot(kind='line', marker='o', ax=ax, color='green', linewidth=2)
        ax.set_title('Score Progression Over Questions')
        ax.set_xlabel('Question Index')
        ax.set_ylabel('Score')
        ax.set_ylim(0, 10)
        ax.grid(True, linestyle='--', alpha=0.6)
        return self._fig_to_bytes(fig)

    def generate_difficulty_chart(self, difficulty_series: pd.Series) -> bytes:
        fig, ax = plt.subplots(figsize=(6, 4))
        difficulty_series.plot(kind='bar', ax=ax, color='orange', edgecolor='black')
        ax.set_title('Average Score by Difficulty')
        ax.set_xlabel('Difficulty Level')
        ax.set_ylabel('Average Score')
        ax.set_ylim(0, 100)
        return self._fig_to_bytes(fig)

    def generate_response_time_chart(self, time_series: pd.Series) -> bytes:
        fig, ax = plt.subplots(figsize=(6, 4))
        time_series.plot(kind='barh', ax=ax, color='purple', edgecolor='black')
        ax.set_title('Average Response Time by Topic (seconds)')
        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel('Topics')
        return self._fig_to_bytes(fig)