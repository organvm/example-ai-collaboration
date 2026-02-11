"""Tests for the CollaborationSession model."""

from __future__ import annotations

import json
import pytest

from src.session import (
    CollaborationSession,
    ContributorType,
    Participant,
    SessionState,
    Turn,
)


@pytest.fixture
def participants() -> list[Participant]:
    return [
        Participant(name="Alice", role=ContributorType.HUMAN),
        Participant(name="GPT-4", role=ContributorType.AI, model="gpt-4"),
    ]


@pytest.fixture
def session(participants: list[Participant]) -> CollaborationSession:
    return CollaborationSession(
        title="Test Session",
        participants=participants,
        session_id="test-session-001",
    )


class TestSessionCreation:
    def test_creates_with_title_and_id(self, session: CollaborationSession) -> None:
        assert session.title == "Test Session"
        assert session.id == "test-session-001"

    def test_initial_state_is_open(self, session: CollaborationSession) -> None:
        assert session.state == SessionState.OPEN

    def test_auto_generates_id_when_not_provided(self) -> None:
        s = CollaborationSession(title="Auto ID")
        assert s.id is not None
        assert len(s.id) > 0

    def test_has_participants(self, session: CollaborationSession) -> None:
        assert len(session.participants) == 2
        assert session.participants[0].name == "Alice"
        assert session.participants[1].model == "gpt-4"


class TestAddTurns:
    def test_add_human_turn(self, session: CollaborationSession) -> None:
        turn = session.add_turn(
            contributor="Alice",
            contributor_type=ContributorType.HUMAN,
            content="Hello, AI!",
        )
        assert turn.contributor == "Alice"
        assert turn.contributor_type == ContributorType.HUMAN
        assert turn.content == "Hello, AI!"
        assert session.total_turns() == 1

    def test_add_ai_turn_with_parent(self, session: CollaborationSession) -> None:
        t1 = session.add_turn(
            contributor="Alice",
            contributor_type=ContributorType.HUMAN,
            content="Prompt",
        )
        t2 = session.add_turn(
            contributor="GPT-4",
            contributor_type=ContributorType.AI,
            content="Response",
            parent_turn_id=t1.id,
        )
        assert t2.parent_turn_id == t1.id
        assert session.total_turns() == 2

    def test_rejects_unknown_contributor(self, session: CollaborationSession) -> None:
        with pytest.raises(ValueError, match="Unknown contributor"):
            session.add_turn(
                contributor="Unknown",
                contributor_type=ContributorType.HUMAN,
                content="Test",
            )

    def test_rejects_invalid_parent_turn(self, session: CollaborationSession) -> None:
        with pytest.raises(ValueError, match="does not exist"):
            session.add_turn(
                contributor="Alice",
                contributor_type=ContributorType.HUMAN,
                content="Test",
                parent_turn_id="nonexistent-id",
            )

    def test_rejects_turn_when_closed(self, session: CollaborationSession) -> None:
        session.transition_to(SessionState.CLOSED)
        with pytest.raises(ValueError, match="must be OPEN"):
            session.add_turn(
                contributor="Alice",
                contributor_type=ContributorType.HUMAN,
                content="Too late",
            )

    def test_word_count(self, session: CollaborationSession) -> None:
        session.add_turn(
            contributor="Alice",
            contributor_type=ContributorType.HUMAN,
            content="one two three four five",
        )
        assert session.total_word_count() == 5


class TestLifecycleTransitions:
    def test_open_to_reviewing(self, session: CollaborationSession) -> None:
        session.transition_to(SessionState.REVIEWING)
        assert session.state == SessionState.REVIEWING

    def test_open_to_closed(self, session: CollaborationSession) -> None:
        session.transition_to(SessionState.CLOSED)
        assert session.state == SessionState.CLOSED
        assert session.closed_at is not None

    def test_reviewing_to_closed(self, session: CollaborationSession) -> None:
        session.transition_to(SessionState.REVIEWING)
        session.transition_to(SessionState.CLOSED)
        assert session.state == SessionState.CLOSED

    def test_reviewing_to_open(self, session: CollaborationSession) -> None:
        session.transition_to(SessionState.REVIEWING)
        session.transition_to(SessionState.OPEN)
        assert session.state == SessionState.OPEN

    def test_closed_is_terminal(self, session: CollaborationSession) -> None:
        session.transition_to(SessionState.CLOSED)
        with pytest.raises(ValueError, match="Invalid transition"):
            session.transition_to(SessionState.OPEN)

    def test_invalid_transition_raises(self, session: CollaborationSession) -> None:
        # OPEN -> OPEN is not a valid transition
        with pytest.raises(ValueError, match="Invalid transition"):
            session.transition_to(SessionState.OPEN)


class TestSerialization:
    def test_to_dict_and_back(self, session: CollaborationSession) -> None:
        session.add_turn(
            contributor="Alice",
            contributor_type=ContributorType.HUMAN,
            content="Test content",
        )
        session.add_turn(
            contributor="GPT-4",
            contributor_type=ContributorType.AI,
            content="AI response",
        )

        data = session.to_dict()
        restored = CollaborationSession.from_dict(data)

        assert restored.id == session.id
        assert restored.title == session.title
        assert len(restored.participants) == len(session.participants)
        assert len(restored.turns) == len(session.turns)
        assert restored.state == session.state

    def test_json_serializable(self, session: CollaborationSession) -> None:
        session.add_turn(
            contributor="Alice",
            contributor_type=ContributorType.HUMAN,
            content="Test",
        )
        data = session.to_dict()
        json_str = json.dumps(data)
        parsed = json.loads(json_str)
        assert parsed["title"] == "Test Session"

    def test_closed_session_serialization(self, session: CollaborationSession) -> None:
        session.transition_to(SessionState.CLOSED)
        data = session.to_dict()
        restored = CollaborationSession.from_dict(data)
        assert restored.state == SessionState.CLOSED
        assert restored.closed_at is not None


class TestTurnWordCount:
    def test_empty_content(self) -> None:
        from datetime import datetime, timezone
        turn = Turn(
            id="t1",
            contributor="Alice",
            contributor_type=ContributorType.HUMAN,
            content="",
            timestamp=datetime.now(timezone.utc),
        )
        # "".split() returns [], len([]) == 0
        assert turn.word_count() == 0

    def test_multiword_content(self) -> None:
        from datetime import datetime, timezone
        turn = Turn(
            id="t2",
            contributor="Alice",
            contributor_type=ContributorType.HUMAN,
            content="The quick brown fox jumps over the lazy dog",
            timestamp=datetime.now(timezone.utc),
        )
        assert turn.word_count() == 9
