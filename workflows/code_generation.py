"""Code generation workflow with human review and testing.

Simulates the AI-conductor pattern for collaborative code creation:
human describes function, AI generates code, human reviews/modifies,
tests are added.
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


# Pre-scripted code review interactions
_CODE_DEMO_SCRIPTS: list[dict[str, str]] = [
    {
        "prompt": (
            "Write a Python function called 'deduplicate_preserving_order' "
            "that removes duplicates from a list while preserving the original "
            "order of first occurrences."
        ),
        "decision": "revise",
        "revision": (
            "from typing import TypeVar, Sequence\n\n"
            "T = TypeVar('T')\n\n\n"
            "def deduplicate_preserving_order(items: Sequence[T]) -> list[T]:\n"
            '    """Remove duplicates while preserving first-occurrence order.\n\n'
            "    Args:\n"
            "        items: Input sequence that may contain duplicates.\n\n"
            "    Returns:\n"
            "        New list with duplicates removed, order preserved.\n\n"
            "    Examples:\n"
            "        >>> deduplicate_preserving_order([3, 1, 4, 1, 5, 9, 2, 6, 5])\n"
            "        [3, 1, 4, 5, 9, 2, 6]\n"
            '    """\n'
            "    seen: set[T] = set()\n"
            "    result: list[T] = []\n"
            "    for item in items:\n"
            "        if item not in seen:\n"
            "            seen.add(item)\n"
            "            result.append(item)\n"
            "    return result\n"
        ),
        "notes": "Added type hints, TypeVar for generic support, docstring with example.",
    },
    {
        "prompt": (
            "Now write comprehensive tests for deduplicate_preserving_order "
            "covering edge cases: empty list, single element, all duplicates, "
            "no duplicates, mixed types."
        ),
        "decision": "accept",
        "notes": "Test coverage is adequate. AI-generated tests look correct.",
    },
    {
        "prompt": (
            "Write a function 'chunk_iterable' that splits any iterable into "
            "chunks of a given size. The last chunk may be smaller."
        ),
        "decision": "revise",
        "revision": (
            "from typing import TypeVar, Iterator, Iterable\n"
            "from itertools import islice\n\n"
            "T = TypeVar('T')\n\n\n"
            "def chunk_iterable(iterable: Iterable[T], size: int) -> Iterator[list[T]]:\n"
            '    """Split an iterable into chunks of the given size.\n\n'
            "    The last chunk may contain fewer than 'size' elements.\n\n"
            "    Args:\n"
            "        iterable: Input iterable to chunk.\n"
            "        size: Maximum number of elements per chunk. Must be >= 1.\n\n"
            "    Yields:\n"
            "        Lists of up to 'size' elements.\n\n"
            "    Raises:\n"
            "        ValueError: If size < 1.\n"
            '    """\n'
            "    if size < 1:\n"
            '        raise ValueError(f"Chunk size must be >= 1, got {size}")\n'
            "    iterator = iter(iterable)\n"
            "    while True:\n"
            "        chunk = list(islice(iterator, size))\n"
            "        if not chunk:\n"
            "            break\n"
            "        yield chunk\n"
        ),
        "notes": "Used islice for memory efficiency. Added input validation.",
    },
    {
        "prompt": "Write tests for chunk_iterable covering size=1, size>len, generators.",
        "decision": "accept",
        "notes": "Tests cover the key edge cases. Accepting AI output.",
    },
]


class CodeGenerationWorkflow:
    """Orchestrates an iterative code generation workflow.

    Runs a multi-turn session where the human describes desired functions,
    the AI generates code, and the human reviews with accept/revise/reject
    decisions. Uses pre-scripted interactions for deterministic demos.
    """

    def __init__(
        self,
        title: str = "Code Generation Session",
        human_name: str = "Developer",
        ai_name: str = "AI Code Assistant",
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

    def run(self, num_turns: int | None = None) -> CollaborationSession:
        """Run the code generation workflow.

        Args:
            num_turns: Number of prompt-response-review cycles. If None,
                runs all available demo scripts.

        Returns:
            The completed CollaborationSession.
        """
        turns_to_run = min(
            num_turns if num_turns is not None else len(_CODE_DEMO_SCRIPTS),
            len(_CODE_DEMO_SCRIPTS),
        )

        for i in range(turns_to_run):
            script = _CODE_DEMO_SCRIPTS[i]

            decision = ConductorDecision(script["decision"])
            revised = script.get("revision")

            self.conductor.run_cycle(
                prompt=script["prompt"],
                decision=decision,
                revised_content=revised,
                review_notes=script.get("notes"),
                response_type="code",
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
