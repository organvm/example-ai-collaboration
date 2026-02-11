"""Session metrics computation for collaboration analysis.

Provides quantitative measures of collaboration dynamics: turn counts,
word counts, human-AI ratios, edit distances, and co-creation percentages.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .attribution import (
    AttributionCategory,
    AttributionTracker,
)
from .session import CollaborationSession, ContributorType


@dataclass
class SessionMetrics:
    """Computed metrics for a collaboration session.

    Attributes:
        total_turns: Total number of turns in the session.
        human_turns: Number of turns by human participants.
        ai_turns: Number of turns by AI participants.
        human_word_count: Total words contributed by humans.
        ai_word_count: Total words contributed by AI.
        total_word_count: Total words across all turns.
        human_ai_ratio: Ratio of human turns to AI turns (inf if no AI turns).
        avg_edit_distance: Mean normalized edit distance across attributed turns.
        session_duration: Session duration in seconds, or None if ongoing.
        co_creation_percentage: Percentage of attributed turns classified as CO_CREATED.
    """

    total_turns: int
    human_turns: int
    ai_turns: int
    human_word_count: int
    ai_word_count: int
    total_word_count: int
    human_ai_ratio: float
    avg_edit_distance: float
    session_duration: float | None
    co_creation_percentage: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_turns": self.total_turns,
            "human_turns": self.human_turns,
            "ai_turns": self.ai_turns,
            "human_word_count": self.human_word_count,
            "ai_word_count": self.ai_word_count,
            "total_word_count": self.total_word_count,
            "human_ai_ratio": self.human_ai_ratio,
            "avg_edit_distance": round(self.avg_edit_distance, 4),
            "session_duration": self.session_duration,
            "co_creation_percentage": round(self.co_creation_percentage, 2),
        }

    def summary_lines(self) -> list[str]:
        """Return a list of human-readable summary lines."""
        lines = [
            f"Total turns: {self.total_turns}",
            f"  Human: {self.human_turns} | AI: {self.ai_turns}",
            f"Total words: {self.total_word_count:,}",
            f"  Human: {self.human_word_count:,} | AI: {self.ai_word_count:,}",
            f"Human-AI ratio: {self.human_ai_ratio:.2f}",
            f"Avg edit distance: {self.avg_edit_distance:.1%}",
            f"Co-creation: {self.co_creation_percentage:.1f}%",
        ]
        if self.session_duration is not None:
            minutes = self.session_duration / 60
            lines.append(f"Duration: {minutes:.1f} minutes")
        return lines


def calculate_metrics(
    session: CollaborationSession,
    tracker: AttributionTracker,
) -> SessionMetrics:
    """Compute metrics for a collaboration session.

    Args:
        session: The session to analyze.
        tracker: Attribution tracker with records for the session's turns.

    Returns:
        SessionMetrics with all computed values.
    """
    human_turns = [
        t for t in session.turns if t.contributor_type == ContributorType.HUMAN
    ]
    ai_turns = [
        t for t in session.turns if t.contributor_type == ContributorType.AI
    ]

    human_turn_count = len(human_turns)
    ai_turn_count = len(ai_turns)

    human_words = sum(t.word_count() for t in human_turns)
    ai_words = sum(t.word_count() for t in ai_turns)

    # Human-AI ratio
    if ai_turn_count > 0:
        ratio = human_turn_count / ai_turn_count
    else:
        ratio = float("inf") if human_turn_count > 0 else 0.0

    # Average edit distance
    distances = tracker.edit_distances()
    if distances:
        avg_edit = sum(distances.values()) / len(distances)
    else:
        avg_edit = 0.0

    # Co-creation percentage
    records = tracker.all_records()
    if records:
        co_created_count = sum(
            1 for r in records if r.category == AttributionCategory.CO_CREATED
        )
        co_creation_pct = (co_created_count / len(records)) * 100
    else:
        co_creation_pct = 0.0

    return SessionMetrics(
        total_turns=session.total_turns(),
        human_turns=human_turn_count,
        ai_turns=ai_turn_count,
        human_word_count=human_words,
        ai_word_count=ai_words,
        total_word_count=human_words + ai_words,
        human_ai_ratio=ratio,
        avg_edit_distance=avg_edit,
        session_duration=session.duration_seconds(),
        co_creation_percentage=co_creation_pct,
    )
