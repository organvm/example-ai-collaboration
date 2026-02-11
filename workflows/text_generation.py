"""Text generation workflow with iterative human review.

Simulates the AI-conductor pattern for collaborative text creation:
human provides topic, AI drafts, human reviews and edits, repeat.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow running from repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.attribution import AttributionTracker
from src.conductor import AIConductor, ConductorDecision
from src.export import export_to_markdown, export_summary
from src.metrics import calculate_metrics, SessionMetrics
from src.session import CollaborationSession, SessionState


# Pre-scripted human edits for deterministic demos
_DEMO_EDITS: list[dict[str, str]] = [
    {
        "prompt": (
            "Write an introduction to the future of AI-human collaboration. "
            "Focus on the conductor model where humans direct and AI generates."
        ),
        "decision": "revise",
        "revision": (
            "The future of AI-human collaboration lies not in replacement but "
            "in orchestration. The conductor model positions the human as "
            "creative director — setting vision, making judgment calls, and "
            "curating output — while AI provides generative capacity at scale. "
            "This mirrors centuries of creative partnerships: the architect and "
            "the builder, the composer and the orchestra."
        ),
        "notes": "Tightened prose, added concrete analogies, removed generic phrasing.",
    },
    {
        "prompt": (
            "Now explore the attribution challenge: when human and AI "
            "collaborate, who is the author?"
        ),
        "decision": "accept",
        "notes": "AI draft captures the nuance well. Accepted with minor satisfaction.",
    },
    {
        "prompt": (
            "Discuss practical implications for creative professionals. "
            "How does the conductor model change daily workflows?"
        ),
        "decision": "revise",
        "revision": (
            "For creative professionals, the conductor model compresses "
            "iteration cycles dramatically. A writer who once spent hours on "
            "first drafts can now generate multiple alternatives in minutes, "
            "then invest that saved time in the higher-order work of selection, "
            "refinement, and voice consistency. The bottleneck shifts from "
            "production to curation — a fundamentally different skill set that "
            "rewards taste, judgment, and strategic thinking."
        ),
        "notes": "Replaced abstract claims with concrete workflow examples.",
    },
    {
        "prompt": (
            "Address the risks: what can go wrong with AI-conductor "
            "collaboration?"
        ),
        "decision": "revise",
        "revision": (
            "The risks of AI-conductor collaboration cluster around three "
            "failure modes. First, automation complacency: humans accept AI "
            "output uncritically, eroding quality over time. Second, voice "
            "homogenization: over-reliance on AI templates produces content "
            "that reads like everything else. Third, attribution opacity: "
            "without rigorous tracking, the provenance of ideas becomes "
            "murky, undermining both credit and accountability."
        ),
        "notes": "Structured as three distinct failure modes for clarity.",
    },
    {
        "prompt": "Conclude with a vision statement for ethical AI collaboration.",
        "decision": "accept",
        "notes": "The AI conclusion resonated. Minimal changes needed.",
    },
]


class TextGenerationWorkflow:
    """Orchestrates an iterative text generation workflow.

    Runs a multi-turn session where the human provides prompts, the AI
    generates drafts, and the human reviews with accept/revise/reject
    decisions. Uses pre-scripted interactions for deterministic demos.
    """

    def __init__(
        self,
        title: str = "Text Generation Session",
        human_name: str = "Writer",
        ai_name: str = "AI Draft Assistant",
    ) -> None:
        self.session = CollaborationSession(title=title)
        self.tracker = AttributionTracker()
        self.conductor = AIConductor(
            session=self.session,
            tracker=self.tracker,
            model="mock",
            human_name=human_name,
            ai_name=ai_name,
        )

    def run(self, num_turns: int = 5) -> CollaborationSession:
        """Run the text generation workflow.

        Args:
            num_turns: Number of prompt-response-review cycles to execute.
                Capped at the number of available demo scripts.

        Returns:
            The completed CollaborationSession.
        """
        turns_to_run = min(num_turns, len(_DEMO_EDITS))

        for i in range(turns_to_run):
            script = _DEMO_EDITS[i]

            decision = ConductorDecision(script["decision"])
            revised = script.get("revision")

            self.conductor.run_cycle(
                prompt=script["prompt"],
                decision=decision,
                revised_content=revised,
                review_notes=script.get("notes"),
                response_type="text",
            )

        # Close the session
        self.session.transition_to(SessionState.REVIEWING)
        self.session.transition_to(SessionState.CLOSED)

        return self.session

    def get_metrics(self) -> SessionMetrics:
        """Compute and return session metrics."""
        return calculate_metrics(self.session, self.tracker)

    def export_markdown(self) -> str:
        """Export the session as a markdown process document."""
        return export_to_markdown(self.session, self.tracker)

    def export_summary_text(self) -> str:
        """Export a short summary."""
        return export_summary(self.session, self.tracker)
