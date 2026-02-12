"""AI conductor for managing prompt-response-review cycles.

The conductor orchestrates the interaction pattern where a human provides
a prompt, an AI generates a response, and the human reviews and decides
whether to accept, revise, or reject the output.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from .attribution import AttributionTracker
from .session import (
    CollaborationSession,
    ContributorType,
    Participant,
    Turn,
)


class ConductorDecision(Enum):
    """Human reviewer's decision on AI-generated content."""

    ACCEPT = "accept"
    REVISE = "revise"
    REJECT = "reject"


@dataclass
class ConductorCycle:
    """A single prompt -> response -> review cycle.

    Tracks the complete lifecycle of one AI generation attempt,
    including the human prompt, AI response, review decision,
    and final content (if accepted or revised).
    """

    cycle_id: int
    prompt_turn_id: str
    response_turn_id: str | None = None
    review_turn_id: str | None = None
    decision: ConductorDecision | None = None
    final_content: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "cycle_id": self.cycle_id,
            "prompt_turn_id": self.prompt_turn_id,
            "response_turn_id": self.response_turn_id,
            "review_turn_id": self.review_turn_id,
            "decision": self.decision.value if self.decision else None,
            "final_content": self.final_content,
        }


# Mock response templates for demonstration purposes
_MOCK_TEXT_TEMPLATES: list[str] = [
    (
        "Based on the prompt about '{topic}', here is a thoughtful exploration. "
        "The intersection of human creativity and artificial intelligence represents "
        "one of the most fascinating developments in modern technology. When we "
        "consider the ways in which AI can augment human capabilities, we find that "
        "the most productive outcomes emerge from genuine collaboration rather than "
        "replacement. The key insight is that AI excels at pattern recognition and "
        "volume generation, while humans bring contextual understanding, emotional "
        "intelligence, and aesthetic judgment. Together, these complementary strengths "
        "create a conductor model where human direction meets AI execution."
    ),
    (
        "Exploring '{topic}' reveals several important dimensions. First, we must "
        "consider the historical context: tools have always shaped creative output, "
        "from the printing press to digital audio workstations. AI represents the "
        "next evolution in this lineage. Second, the question of attribution becomes "
        "critical — when a human directs an AI to produce content, who is the author? "
        "The answer lies in understanding collaboration as a spectrum rather than a "
        "binary. Third, the practical implications for creative workflows are "
        "substantial: iteration cycles compress, exploration space expands, and the "
        "barrier to initial drafts drops significantly."
    ),
    (
        "The topic of '{topic}' invites us to reconsider fundamental assumptions "
        "about creativity and authorship. In the AI-conductor model, the human "
        "serves as director, curator, and quality arbiter while the AI provides "
        "generative capacity. This division of labor mirrors historical creative "
        "partnerships — think of a film director working with actors, or a composer "
        "working with an orchestra. The conductor does not diminish the performers; "
        "rather, the conductor channels collective capability toward a unified vision."
    ),
]

_MOCK_CODE_TEMPLATES: list[str] = [
    (
        "def {func_name}(data: list[Any]) -> dict[str, Any]:\n"
        '    """Process the input data and return structured results.\n\n'
        "    Args:\n"
        "        data: Input data to process.\n\n"
        "    Returns:\n"
        "        Dictionary containing processed results.\n"
        '    """\n'
        "    results: dict[str, Any] = {{}}\n"
        "    for item in data:\n"
        "        key = str(item)\n"
        "        results[key] = len(str(item))\n"
        "    return results\n"
    ),
    (
        "class {func_name}:\n"
        '    """Handler for processing structured data.\n\n'
        "    Provides methods for validation, transformation,\n"
        "    and output formatting.\n"
        '    """\n\n'
        "    def __init__(self, config: dict[str, Any] | None = None) -> None:\n"
        "        self.config = config or {{}}\n"
        "        self._cache: dict[str, Any] = {{}}\n\n"
        "    def process(self, input_data: str) -> str:\n"
        '        """Process input and return formatted output."""\n'
        "        return input_data.strip().lower()\n"
    ),
]


class AIConductor:
    """Orchestrates prompt -> response -> review cycles.

    In mock mode (default), generates plausible responses from templates.
    Tracks the full cycle including conductor decisions.

    Args:
        session: The collaboration session to operate within.
        tracker: Attribution tracker for recording contributions.
        model: Model identifier. Use "mock" for template-based responses.
        human_name: Name of the human participant.
        ai_name: Name of the AI participant.
    """

    def __init__(
        self,
        session: CollaborationSession,
        tracker: AttributionTracker,
        model: str = "mock",
        human_name: str = "Human",
        ai_name: str = "AI Assistant",
    ) -> None:
        self.session = session
        self.tracker = tracker
        self.model = model
        self.human_name = human_name
        self.ai_name = ai_name
        self.cycles: list[ConductorCycle] = []
        self._cycle_counter: int = 0

        # Ensure participants are registered
        participant_names = {p.name for p in session.participants}
        if human_name not in participant_names:
            session.add_participant(
                Participant(name=human_name, role=ContributorType.HUMAN)
            )
        if ai_name not in participant_names:
            session.add_participant(
                Participant(name=ai_name, role=ContributorType.AI, model=model)
            )

    def submit_prompt(self, prompt: str) -> Turn:
        """Human submits a prompt, starting a new cycle.

        Returns the prompt turn.
        """
        turn = self.session.add_turn(
            contributor=self.human_name,
            contributor_type=ContributorType.HUMAN,
            content=prompt,
        )
        self.tracker.record_human_only(turn.id, prompt)

        self._cycle_counter += 1
        cycle = ConductorCycle(
            cycle_id=self._cycle_counter,
            prompt_turn_id=turn.id,
        )
        self.cycles.append(cycle)
        return turn

    def generate_response(
        self,
        prompt_turn: Turn | None = None,
        response_type: str = "text",
    ) -> Turn:
        """AI generates a response to the most recent prompt.

        Args:
            prompt_turn: The prompt turn to respond to. If None, uses the
                most recent prompt.
            response_type: Either "text" or "code" for mock template selection.

        Returns:
            The AI response turn.
        """
        if not self.cycles:
            raise ValueError("No active cycle. Call submit_prompt() first.")

        current_cycle = self.cycles[-1]

        if prompt_turn is None:
            # Find the prompt turn
            prompt_turn = next(
                (t for t in self.session.turns if t.id == current_cycle.prompt_turn_id),
                None,
            )

        if prompt_turn is None:
            raise ValueError("Could not find prompt turn for current cycle.")

        content = self._generate_mock_response(
            prompt_turn.content, response_type
        )

        turn = self.session.add_turn(
            contributor=self.ai_name,
            contributor_type=ContributorType.AI,
            content=content,
            parent_turn_id=prompt_turn.id,
        )
        self.tracker.record_ai_output(turn.id, content)

        current_cycle.response_turn_id = turn.id
        return turn

    def review(
        self,
        decision: ConductorDecision,
        revised_content: str | None = None,
        review_notes: str | None = None,
    ) -> Turn:
        """Human reviews the AI response and makes a decision.

        Args:
            decision: Accept, revise, or reject.
            revised_content: If revising, the human-edited version.
            review_notes: Optional notes explaining the decision.

        Returns:
            The review turn.
        """
        if not self.cycles:
            raise ValueError("No active cycle.")

        current_cycle = self.cycles[-1]
        if current_cycle.response_turn_id is None:
            raise ValueError(
                "No AI response to review. Call generate_response() first."
            )

        current_cycle.decision = decision

        if decision == ConductorDecision.ACCEPT:
            # Find the AI response content
            response_turn = next(
                (t for t in self.session.turns if t.id == current_cycle.response_turn_id),
                None,
            )
            final = response_turn.content if response_turn else ""
            review_text = review_notes or "Accepted AI output without modification."
        elif decision == ConductorDecision.REVISE:
            if revised_content is None:
                raise ValueError("Must provide revised_content when decision is REVISE.")
            final = revised_content
            review_text = review_notes or "Revised AI output with human edits."
        else:  # REJECT
            final = ""
            review_text = review_notes or "Rejected AI output."

        current_cycle.final_content = final

        turn = self.session.add_turn(
            contributor=self.human_name,
            contributor_type=ContributorType.HUMAN,
            content=review_text,
            parent_turn_id=current_cycle.response_turn_id,
            metadata={"decision": decision.value, "final_content": final},
        )

        # Record the final version for attribution tracking
        if current_cycle.response_turn_id:
            self.tracker.record_final_version(
                current_cycle.response_turn_id, final
            )

        current_cycle.review_turn_id = turn.id
        return turn

    def run_cycle(
        self,
        prompt: str,
        decision: ConductorDecision = ConductorDecision.ACCEPT,
        revised_content: str | None = None,
        review_notes: str | None = None,
        response_type: str = "text",
    ) -> ConductorCycle:
        """Run a complete prompt -> response -> review cycle.

        Convenience method that chains submit_prompt, generate_response,
        and review.

        Returns:
            The completed cycle record.
        """
        self.submit_prompt(prompt)
        self.generate_response(response_type=response_type)
        self.review(
            decision=decision,
            revised_content=revised_content,
            review_notes=review_notes,
        )
        return self.cycles[-1]

    def _generate_mock_response(self, prompt: str, response_type: str) -> str:
        """Generate a mock response from templates."""
        if self.model != "mock":
            raise NotImplementedError(
                f"Model '{self.model}' is not implemented. Use 'mock' for demos."
            )

        # Extract a topic hint from the prompt
        words = prompt.split()
        topic = " ".join(words[:8]) if len(words) > 8 else prompt

        if response_type == "code":
            # Generate a function name from prompt words
            func_words = [w.lower() for w in words[:3] if w.isalpha()]
            func_name = "_".join(func_words) if func_words else "process_data"
            template = random.choice(_MOCK_CODE_TEMPLATES)
            return template.format(func_name=func_name)
        else:
            template = random.choice(_MOCK_TEXT_TEMPLATES)
            return template.format(topic=topic)
