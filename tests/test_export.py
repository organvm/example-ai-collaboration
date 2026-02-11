"""Tests for export functions (markdown, JSON, summary)."""

from __future__ import annotations

import json

from src.attribution import AttributionTracker
from src.export import export_to_json, export_to_markdown, export_summary
from src.session import (
    CollaborationSession,
    ContributorType,
    Participant,
    SessionState,
)


def _create_test_session() -> tuple[CollaborationSession, AttributionTracker]:
    """Create a test session with a few turns and attribution data."""
    session = CollaborationSession(
        title="Export Test Session",
        participants=[
            Participant(name="Alice", role=ContributorType.HUMAN),
            Participant(name="Bot", role=ContributorType.AI, model="mock"),
        ],
        session_id="export-test-001",
    )
    tracker = AttributionTracker()

    # Turn 1: human prompt
    t1 = session.add_turn(
        contributor="Alice",
        contributor_type=ContributorType.HUMAN,
        content="Write about testing.",
    )
    tracker.record_human_only(t1.id, t1.content)

    # Turn 2: AI response
    ai_content = "Testing is a critical part of software development."
    t2 = session.add_turn(
        contributor="Bot",
        contributor_type=ContributorType.AI,
        content=ai_content,
        parent_turn_id=t1.id,
    )
    tracker.record_ai_output(t2.id, ai_content)
    tracker.record_final_version(t2.id, ai_content)  # Accepted verbatim

    # Turn 3: human review
    t3 = session.add_turn(
        contributor="Alice",
        contributor_type=ContributorType.HUMAN,
        content="Looks good, accepted.",
        metadata={"decision": "accept"},
    )
    tracker.record_human_only(t3.id, t3.content)

    session.transition_to(SessionState.CLOSED)
    return session, tracker


class TestExportToMarkdown:
    def test_contains_title(self) -> None:
        session, tracker = _create_test_session()
        md = export_to_markdown(session, tracker)
        assert "# Export Test Session" in md

    def test_contains_participants(self) -> None:
        session, tracker = _create_test_session()
        md = export_to_markdown(session, tracker)
        assert "Alice" in md
        assert "Bot" in md
        assert "mock" in md

    def test_contains_turns(self) -> None:
        session, tracker = _create_test_session()
        md = export_to_markdown(session, tracker)
        assert "Turn 1:" in md
        assert "Turn 2:" in md
        assert "Turn 3:" in md

    def test_contains_attribution(self) -> None:
        session, tracker = _create_test_session()
        md = export_to_markdown(session, tracker)
        assert "Attribution:" in md

    def test_contains_metrics_table(self) -> None:
        session, tracker = _create_test_session()
        md = export_to_markdown(session, tracker)
        assert "Session Metrics" in md
        assert "Total Turns" in md
        assert "Human Turns" in md

    def test_contains_session_state(self) -> None:
        session, tracker = _create_test_session()
        md = export_to_markdown(session, tracker)
        assert "CLOSED" in md

    def test_without_tracker(self) -> None:
        session, _ = _create_test_session()
        md = export_to_markdown(session)
        assert "# Export Test Session" in md
        # Should not have attribution or metrics sections
        assert "Session Metrics" not in md


class TestExportToJson:
    def test_produces_valid_json(self) -> None:
        session, tracker = _create_test_session()
        json_str = export_to_json(session, tracker)
        data = json.loads(json_str)
        assert "session" in data
        assert "attribution" in data
        assert "metrics" in data

    def test_session_data_present(self) -> None:
        session, tracker = _create_test_session()
        json_str = export_to_json(session, tracker)
        data = json.loads(json_str)
        assert data["session"]["title"] == "Export Test Session"
        assert len(data["session"]["turns"]) == 3

    def test_metrics_present(self) -> None:
        session, tracker = _create_test_session()
        json_str = export_to_json(session, tracker)
        data = json.loads(json_str)
        assert data["metrics"]["total_turns"] == 3

    def test_without_tracker(self) -> None:
        session, _ = _create_test_session()
        json_str = export_to_json(session)
        data = json.loads(json_str)
        assert "session" in data
        assert "attribution" not in data


class TestExportSummary:
    def test_contains_title(self) -> None:
        session, tracker = _create_test_session()
        summary = export_summary(session, tracker)
        assert "Export Test Session" in summary

    def test_contains_state(self) -> None:
        session, tracker = _create_test_session()
        summary = export_summary(session, tracker)
        assert "CLOSED" in summary

    def test_contains_participant_names(self) -> None:
        session, tracker = _create_test_session()
        summary = export_summary(session, tracker)
        assert "Alice" in summary
        assert "Bot" in summary

    def test_contains_metrics(self) -> None:
        session, tracker = _create_test_session()
        summary = export_summary(session, tracker)
        assert "Total turns:" in summary

    def test_without_tracker(self) -> None:
        session, _ = _create_test_session()
        summary = export_summary(session)
        assert "Total turns:" in summary
        assert "Total words:" in summary
