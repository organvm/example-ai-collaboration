"""Tests for the AIConductor prompt-response-review cycle."""

from __future__ import annotations

import pytest

from src.attribution import AttributionTracker
from src.conductor import AIConductor, ConductorDecision
from src.session import (
    CollaborationSession,
    ContributorType,
)


@pytest.fixture
def conductor_setup() -> tuple[CollaborationSession, AttributionTracker, AIConductor]:
    """Create a session with conductor ready to use."""
    session = CollaborationSession(title="Conductor Test")
    tracker = AttributionTracker()
    conductor = AIConductor(
        session=session,
        tracker=tracker,
        model="mock",
        human_name="Human",
        ai_name="AI",
    )
    return session, tracker, conductor


class TestConductorSetup:
    def test_registers_participants(
        self, conductor_setup: tuple[CollaborationSession, AttributionTracker, AIConductor]
    ) -> None:
        session, _, _ = conductor_setup
        names = {p.name for p in session.participants}
        assert "Human" in names
        assert "AI" in names

    def test_ai_participant_has_model(
        self, conductor_setup: tuple[CollaborationSession, AttributionTracker, AIConductor]
    ) -> None:
        session, _, _ = conductor_setup
        ai_participant = next(
            p for p in session.participants if p.role == ContributorType.AI
        )
        assert ai_participant.model == "mock"


class TestSubmitPrompt:
    def test_creates_human_turn(
        self, conductor_setup: tuple[CollaborationSession, AttributionTracker, AIConductor]
    ) -> None:
        session, _, conductor = conductor_setup
        turn = conductor.submit_prompt("Write about AI.")
        assert turn.contributor == "Human"
        assert turn.contributor_type == ContributorType.HUMAN
        assert turn.content == "Write about AI."

    def test_starts_new_cycle(
        self, conductor_setup: tuple[CollaborationSession, AttributionTracker, AIConductor]
    ) -> None:
        _, _, conductor = conductor_setup
        conductor.submit_prompt("Test prompt")
        assert len(conductor.cycles) == 1
        assert conductor.cycles[0].cycle_id == 1


class TestGenerateResponse:
    def test_creates_ai_turn(
        self, conductor_setup: tuple[CollaborationSession, AttributionTracker, AIConductor]
    ) -> None:
        session, _, conductor = conductor_setup
        conductor.submit_prompt("Write about collaboration.")
        turn = conductor.generate_response()
        assert turn.contributor == "AI"
        assert turn.contributor_type == ContributorType.AI
        assert len(turn.content) > 0

    def test_response_has_parent(
        self, conductor_setup: tuple[CollaborationSession, AttributionTracker, AIConductor]
    ) -> None:
        _, _, conductor = conductor_setup
        prompt_turn = conductor.submit_prompt("Test")
        response_turn = conductor.generate_response()
        assert response_turn.parent_turn_id == prompt_turn.id

    def test_raises_without_prompt(
        self, conductor_setup: tuple[CollaborationSession, AttributionTracker, AIConductor]
    ) -> None:
        _, _, conductor = conductor_setup
        with pytest.raises(ValueError, match="No active cycle"):
            conductor.generate_response()

    def test_code_response_type(
        self, conductor_setup: tuple[CollaborationSession, AttributionTracker, AIConductor]
    ) -> None:
        _, _, conductor = conductor_setup
        conductor.submit_prompt("Write a function")
        turn = conductor.generate_response(response_type="code")
        assert turn.content  # Non-empty code output

    def test_non_mock_model_raises(self) -> None:
        session = CollaborationSession(title="Non-mock")
        tracker = AttributionTracker()
        conductor = AIConductor(
            session=session, tracker=tracker, model="gpt-4"
        )
        conductor.submit_prompt("Test")
        with pytest.raises(NotImplementedError, match="not implemented"):
            conductor.generate_response()


class TestReview:
    def test_accept_decision(
        self, conductor_setup: tuple[CollaborationSession, AttributionTracker, AIConductor]
    ) -> None:
        _, _, conductor = conductor_setup
        conductor.submit_prompt("Write something.")
        conductor.generate_response()
        turn = conductor.review(ConductorDecision.ACCEPT)
        assert turn.metadata["decision"] == "accept"
        cycle = conductor.cycles[-1]
        assert cycle.decision == ConductorDecision.ACCEPT
        assert cycle.final_content is not None
        assert len(cycle.final_content) > 0

    def test_revise_decision(
        self, conductor_setup: tuple[CollaborationSession, AttributionTracker, AIConductor]
    ) -> None:
        _, _, conductor = conductor_setup
        conductor.submit_prompt("Write something.")
        conductor.generate_response()
        turn = conductor.review(
            ConductorDecision.REVISE,
            revised_content="My custom version.",
            review_notes="Rewrote for clarity.",
        )
        assert turn.metadata["decision"] == "revise"
        cycle = conductor.cycles[-1]
        assert cycle.final_content == "My custom version."

    def test_revise_requires_content(
        self, conductor_setup: tuple[CollaborationSession, AttributionTracker, AIConductor]
    ) -> None:
        _, _, conductor = conductor_setup
        conductor.submit_prompt("Test")
        conductor.generate_response()
        with pytest.raises(ValueError, match="Must provide revised_content"):
            conductor.review(ConductorDecision.REVISE)

    def test_reject_decision(
        self, conductor_setup: tuple[CollaborationSession, AttributionTracker, AIConductor]
    ) -> None:
        _, _, conductor = conductor_setup
        conductor.submit_prompt("Test")
        conductor.generate_response()
        turn = conductor.review(ConductorDecision.REJECT)
        assert turn.metadata["decision"] == "reject"
        cycle = conductor.cycles[-1]
        assert cycle.final_content == ""

    def test_review_without_response_raises(
        self, conductor_setup: tuple[CollaborationSession, AttributionTracker, AIConductor]
    ) -> None:
        _, _, conductor = conductor_setup
        conductor.submit_prompt("Test")
        with pytest.raises(ValueError, match="No AI response"):
            conductor.review(ConductorDecision.ACCEPT)


class TestRunCycle:
    def test_complete_accept_cycle(
        self, conductor_setup: tuple[CollaborationSession, AttributionTracker, AIConductor]
    ) -> None:
        session, tracker, conductor = conductor_setup
        cycle = conductor.run_cycle("Write about AI.")
        assert cycle.decision == ConductorDecision.ACCEPT
        assert cycle.final_content is not None
        # Should have 3 turns: prompt, response, review
        assert session.total_turns() == 3

    def test_complete_revise_cycle(
        self, conductor_setup: tuple[CollaborationSession, AttributionTracker, AIConductor]
    ) -> None:
        _, _, conductor = conductor_setup
        cycle = conductor.run_cycle(
            "Write about AI.",
            decision=ConductorDecision.REVISE,
            revised_content="My version.",
        )
        assert cycle.final_content == "My version."

    def test_multiple_cycles(
        self, conductor_setup: tuple[CollaborationSession, AttributionTracker, AIConductor]
    ) -> None:
        session, _, conductor = conductor_setup
        conductor.run_cycle("First topic")
        conductor.run_cycle("Second topic")
        assert len(conductor.cycles) == 2
        assert session.total_turns() == 6  # 3 per cycle

    def test_attribution_tracked_for_accept(
        self, conductor_setup: tuple[CollaborationSession, AttributionTracker, AIConductor]
    ) -> None:
        _, tracker, conductor = conductor_setup
        cycle = conductor.run_cycle("Test prompt")
        # The AI response turn should have an attribution record
        assert cycle.response_turn_id is not None
        record = tracker.get_record(cycle.response_turn_id)
        assert record is not None

    def test_attribution_tracked_for_revise(
        self, conductor_setup: tuple[CollaborationSession, AttributionTracker, AIConductor]
    ) -> None:
        _, tracker, conductor = conductor_setup
        cycle = conductor.run_cycle(
            "Test",
            decision=ConductorDecision.REVISE,
            revised_content="Completely different text with major changes.",
        )
        assert cycle.response_turn_id is not None
        record = tracker.get_record(cycle.response_turn_id)
        assert record is not None
