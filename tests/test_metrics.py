"""Tests for session metrics computation."""

from __future__ import annotations

from src.attribution import AttributionTracker
from src.metrics import SessionMetrics, calculate_metrics
from src.session import (
    CollaborationSession,
    ContributorType,
    Participant,
    SessionState,
)


def _make_session_with_turns() -> tuple[CollaborationSession, AttributionTracker]:
    """Create a session with known turn data for deterministic metric testing."""
    session = CollaborationSession(
        title="Metrics Test",
        participants=[
            Participant(name="Human", role=ContributorType.HUMAN),
            Participant(name="AI", role=ContributorType.AI, model="mock"),
        ],
        session_id="metrics-test-001",
    )
    tracker = AttributionTracker()

    # Turn 1: human prompt (3 words)
    t1 = session.add_turn(
        contributor="Human",
        contributor_type=ContributorType.HUMAN,
        content="Write about testing",
    )
    tracker.record_human_only(t1.id, t1.content)

    # Turn 2: AI response (6 words), accepted verbatim
    ai_text = "Testing ensures software works correctly always"
    t2 = session.add_turn(
        contributor="AI",
        contributor_type=ContributorType.AI,
        content=ai_text,
        parent_turn_id=t1.id,
    )
    tracker.record_ai_output(t2.id, ai_text)
    tracker.record_final_version(t2.id, ai_text)

    # Turn 3: human review (2 words)
    t3 = session.add_turn(
        contributor="Human",
        contributor_type=ContributorType.HUMAN,
        content="Looks good",
    )
    tracker.record_human_only(t3.id, t3.content)

    # Turn 4: AI response (6 words), heavily edited
    ai_text2 = "Here is more content about the topic"
    t4 = session.add_turn(
        contributor="AI",
        contributor_type=ContributorType.AI,
        content=ai_text2,
        parent_turn_id=t3.id,
    )
    tracker.record_ai_output(t4.id, ai_text2)
    # Heavy edit -> should be HUMAN_AUTHORED
    tracker.record_final_version(
        t4.id,
        "A completely different piece that was rewritten from scratch by the human collaborator"
    )

    return session, tracker


class TestCalculateMetrics:
    def test_total_turns(self) -> None:
        session, tracker = _make_session_with_turns()
        metrics = calculate_metrics(session, tracker)
        assert metrics.total_turns == 4

    def test_human_and_ai_turn_counts(self) -> None:
        session, tracker = _make_session_with_turns()
        metrics = calculate_metrics(session, tracker)
        assert metrics.human_turns == 2
        assert metrics.ai_turns == 2

    def test_word_counts(self) -> None:
        session, tracker = _make_session_with_turns()
        metrics = calculate_metrics(session, tracker)
        # Human: "Write about testing" (3) + "Looks good" (2) = 5
        assert metrics.human_word_count == 5
        # AI: 6 + 7 = 13
        assert metrics.ai_word_count == 13
        assert metrics.total_word_count == 18

    def test_human_ai_ratio(self) -> None:
        session, tracker = _make_session_with_turns()
        metrics = calculate_metrics(session, tracker)
        # 2 human / 2 AI = 1.0
        assert metrics.human_ai_ratio == 1.0

    def test_avg_edit_distance(self) -> None:
        session, tracker = _make_session_with_turns()
        metrics = calculate_metrics(session, tracker)
        # t2: identical (0.0), t4: heavy edit (high distance)
        # Average should be > 0
        assert metrics.avg_edit_distance > 0.0

    def test_co_creation_percentage(self) -> None:
        session, tracker = _make_session_with_turns()
        metrics = calculate_metrics(session, tracker)
        # We have 4 attribution records:
        # t1: HUMAN_AUTHORED, t2: AI_GENERATED, t3: HUMAN_AUTHORED, t4: HUMAN_AUTHORED
        # co_creation_pct = 0% (no CO_CREATED records in this fixture)
        assert metrics.co_creation_percentage == 0.0

    def test_session_duration_when_closed(self) -> None:
        session, tracker = _make_session_with_turns()
        session.transition_to(SessionState.CLOSED)
        metrics = calculate_metrics(session, tracker)
        assert metrics.session_duration is not None
        assert metrics.session_duration >= 0.0


class TestSessionMetrics:
    def test_to_dict(self) -> None:
        metrics = SessionMetrics(
            total_turns=10,
            human_turns=6,
            ai_turns=4,
            human_word_count=500,
            ai_word_count=800,
            total_word_count=1300,
            human_ai_ratio=1.5,
            avg_edit_distance=0.35,
            session_duration=120.0,
            co_creation_percentage=40.0,
        )
        data = metrics.to_dict()
        assert data["total_turns"] == 10
        assert data["human_ai_ratio"] == 1.5
        assert data["co_creation_percentage"] == 40.0

    def test_summary_lines(self) -> None:
        metrics = SessionMetrics(
            total_turns=10,
            human_turns=6,
            ai_turns=4,
            human_word_count=500,
            ai_word_count=800,
            total_word_count=1300,
            human_ai_ratio=1.5,
            avg_edit_distance=0.35,
            session_duration=120.0,
            co_creation_percentage=40.0,
        )
        lines = metrics.summary_lines()
        assert any("Total turns: 10" in line for line in lines)
        assert any("Duration" in line for line in lines)

    def test_summary_without_duration(self) -> None:
        metrics = SessionMetrics(
            total_turns=5,
            human_turns=3,
            ai_turns=2,
            human_word_count=100,
            ai_word_count=200,
            total_word_count=300,
            human_ai_ratio=1.5,
            avg_edit_distance=0.2,
            session_duration=None,
            co_creation_percentage=50.0,
        )
        lines = metrics.summary_lines()
        assert not any("Duration" in line for line in lines)


class TestEdgeCases:
    def test_empty_session(self) -> None:
        session = CollaborationSession(title="Empty")
        tracker = AttributionTracker()
        metrics = calculate_metrics(session, tracker)
        assert metrics.total_turns == 0
        assert metrics.human_ai_ratio == 0.0
        assert metrics.avg_edit_distance == 0.0
        assert metrics.co_creation_percentage == 0.0

    def test_human_only_session(self) -> None:
        session = CollaborationSession(
            title="Human Only",
            participants=[Participant(name="Solo", role=ContributorType.HUMAN)],
        )
        tracker = AttributionTracker()
        t = session.add_turn(
            contributor="Solo",
            contributor_type=ContributorType.HUMAN,
            content="Just me here",
        )
        tracker.record_human_only(t.id, t.content)
        metrics = calculate_metrics(session, tracker)
        assert metrics.human_turns == 1
        assert metrics.ai_turns == 0
        assert metrics.human_ai_ratio == float("inf")
