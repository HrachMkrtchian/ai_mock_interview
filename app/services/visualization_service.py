import io
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd


class VisualizationService:

    @staticmethod
    def _fig_to_bytes(fig) -> bytes:
        try:
            buf = io.BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight', dpi=150)
            buf.seek(0)
            return buf.getvalue()
        finally:
            plt.close(fig)

    def generate_topic_scores_chart(self, topic_series: pd.Series) -> bytes:
        if topic_series.empty:
            return b""

        fig, ax = plt.subplots(figsize=(7, 4.5))
        bars = topic_series.plot(kind='bar', ax=ax, color='#3B82F6', edgecolor='#1E40AF', linewidth=1.2)

        ax.set_title('Average Score by Topic', fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('Topics', fontsize=11, labelpad=10)
        ax.set_ylabel('Score (0-10)', fontsize=11)
        ax.set_ylim(0, 10)
        ax.grid(axis='y', linestyle='--', alpha=0.5)
        plt.xticks(rotation=30, ha='right')
        plt.tight_layout()
        return self._fig_to_bytes(fig)

    def generate_score_progression_chart(self, progression_series: pd.Series) -> bytes:
        if progression_series.empty:
            return b""

        fig, ax = plt.subplots(figsize=(7, 4.5))
        progression_series.plot(kind='line', marker='o', ax=ax, color='#10B981', linewidth=2.5, markersize=8)

        ax.set_title('Score Progression Over Questions', fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('Question Index', fontsize=11, labelpad=10)
        ax.set_ylabel('Score', fontsize=11)
        ax.set_ylim(0, 10)
        ax.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        return self._fig_to_bytes(fig)

    def generate_difficulty_chart(self, difficulty_series: pd.Series) -> bytes:
        if difficulty_series.empty:
            return b""

        fig, ax = plt.subplots(figsize=(7, 4.5))
        difficulty_series.plot(kind='bar', ax=ax, color='#F59E0B', edgecolor='#B45309', linewidth=1.2)

        ax.set_title('Average Score by Difficulty', fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('Difficulty Level', fontsize=11, labelpad=10)
        ax.set_ylabel('Score (0-10)', fontsize=11)
        ax.set_ylim(0, 10)
        ax.grid(axis='y', linestyle='--', alpha=0.5)
        plt.xticks(rotation=0)
        plt.tight_layout()
        return self._fig_to_bytes(fig)

    def generate_response_time_chart(self, time_series: pd.Series) -> bytes:
        if time_series.empty:
            return b""

        fig, ax = plt.subplots(figsize=(7, 4.5))
        time_series.plot(kind='barh', ax=ax, color='#8B5CF6', edgecolor='#6D28D9', linewidth=1.2)

        ax.set_title('Average Response Time (seconds)', fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel('Time (sec)', fontsize=11, labelpad=10)
        ax.set_ylabel('Topics', fontsize=11)
        ax.grid(axis='x', linestyle='--', alpha=0.5)
        plt.tight_layout()
        return self._fig_to_bytes(fig)