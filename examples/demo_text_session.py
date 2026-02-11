#!/usr/bin/env python3
"""Demo: run a text generation collaboration session.

Creates a 5-turn AI-conductor session about "The future of AI-human
collaboration", exports the process document to markdown, and prints
session metrics.

Usage:
    python examples/demo_text_session.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the repo root is on the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from workflows.text_generation import TextGenerationWorkflow


def main() -> None:
    print("=" * 70)
    print("AI-Conductor Text Generation Demo")
    print("=" * 70)
    print()

    # Create and run the workflow
    workflow = TextGenerationWorkflow(
        title="The Future of AI-Human Collaboration",
        human_name="Writer",
        ai_name="AI Draft Assistant",
    )
    session = workflow.run(num_turns=5)

    # Print the markdown export
    markdown = workflow.export_markdown()
    print(markdown)
    print()

    # Print summary
    print("=" * 70)
    print("SESSION SUMMARY")
    print("=" * 70)
    print()
    summary = workflow.export_summary_text()
    print(summary)
    print()

    # Print detailed metrics
    metrics = workflow.get_metrics()
    print("=" * 70)
    print("DETAILED METRICS")
    print("=" * 70)
    print()
    for line in metrics.summary_lines():
        print(f"  {line}")
    print()
    print(f"Session state: {session.state.value}")
    print(f"Session ID: {session.id}")


if __name__ == "__main__":
    main()
