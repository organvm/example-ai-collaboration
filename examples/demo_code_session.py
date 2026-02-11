#!/usr/bin/env python3
"""Demo: run a code generation collaboration session.

Creates an AI-conductor session to collaboratively build Python functions,
exports the process document, and prints session metrics.

Usage:
    python examples/demo_code_session.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the repo root is on the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from workflows.code_generation import CodeGenerationWorkflow


def main() -> None:
    print("=" * 70)
    print("AI-Conductor Code Generation Demo")
    print("=" * 70)
    print()

    # Create and run the workflow
    workflow = CodeGenerationWorkflow(
        title="Utility Function Development Session",
        human_name="Developer",
        ai_name="AI Code Assistant",
    )
    session = workflow.run()

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
