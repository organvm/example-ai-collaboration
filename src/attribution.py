"""Attribution model for classifying AI-human contributions.

Determines whether content was human-authored, AI-generated, or co-created
based on edit distance analysis between AI output and final approved version.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AttributionCategory(Enum):
    """Classification of content authorship."""

    HUMAN_AUTHORED = "HUMAN_AUTHORED"
    AI_GENERATED = "AI_GENERATED"
    CO_CREATED = "CO_CREATED"


@dataclass
class AttributionRecord:
    """Attribution metadata for a single turn or content unit.

    Attributes:
        turn_id: The turn this attribution applies to.
        category: The authorship classification.
        confidence: Confidence score between 0.0 and 1.0.
        evidence: Human-readable explanation of the classification rationale.
    """

    turn_id: str
    category: AttributionCategory
    confidence: float
    evidence: str

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                f"Confidence must be between 0.0 and 1.0, got {self.confidence}"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "turn_id": self.turn_id,
            "category": self.category.value,
            "confidence": self.confidence,
            "evidence": self.evidence,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AttributionRecord:
        return cls(
            turn_id=data["turn_id"],
            category=AttributionCategory(data["category"]),
            confidence=data["confidence"],
            evidence=data["evidence"],
        )


def _levenshtein_distance(s1: str, s2: str) -> int:
    """Compute the Levenshtein edit distance between two strings.

    Uses the classic dynamic-programming approach. Operates on characters,
    not tokens, for simplicity and determinism.
    """
    if len(s1) < len(s2):
        return _levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = list(range(len(s2) + 1))

    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            # Cost is 0 if characters match, 1 otherwise
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def normalized_edit_distance(original: str, modified: str) -> float:
    """Compute edit distance normalized to [0.0, 1.0].

    Returns the ratio of edits to the length of the longer string.
    A value of 0.0 means the strings are identical.
    A value of 1.0 means complete replacement.
    """
    if not original and not modified:
        return 0.0
    max_len = max(len(original), len(modified))
    if max_len == 0:
        return 0.0
    distance = _levenshtein_distance(original, modified)
    return min(distance / max_len, 1.0)


# Thresholds for attribution classification
_AI_GENERATED_THRESHOLD = 0.10  # < 10% edit distance -> AI_GENERATED
_CO_CREATED_THRESHOLD = 0.60   # 10-60% -> CO_CREATED, > 60% -> HUMAN_AUTHORED


def classify_attribution(
    ai_output: str,
    final_version: str,
) -> tuple[AttributionCategory, float, str]:
    """Classify content based on edit distance between AI output and final version.

    Rules:
        - Edit distance < 10%  -> AI_GENERATED
        - Edit distance 10-60% -> CO_CREATED
        - Edit distance > 60%  -> HUMAN_AUTHORED

    Returns:
        Tuple of (category, confidence, evidence).
    """
    edit_dist = normalized_edit_distance(ai_output, final_version)

    if edit_dist < _AI_GENERATED_THRESHOLD:
        category = AttributionCategory.AI_GENERATED
        confidence = 1.0 - (edit_dist / _AI_GENERATED_THRESHOLD)
        evidence = (
            f"Edit distance {edit_dist:.1%} is below the {_AI_GENERATED_THRESHOLD:.0%} "
            f"threshold. Content was accepted with minimal or no modification."
        )
    elif edit_dist <= _CO_CREATED_THRESHOLD:
        category = AttributionCategory.CO_CREATED
        # Confidence peaks at the midpoint of the co-created range
        midpoint = (_AI_GENERATED_THRESHOLD + _CO_CREATED_THRESHOLD) / 2
        distance_from_mid = abs(edit_dist - midpoint)
        range_half = (_CO_CREATED_THRESHOLD - _AI_GENERATED_THRESHOLD) / 2
        confidence = 1.0 - (distance_from_mid / range_half) * 0.4
        evidence = (
            f"Edit distance {edit_dist:.1%} falls in the co-creation range "
            f"({_AI_GENERATED_THRESHOLD:.0%}-{_CO_CREATED_THRESHOLD:.0%}). "
            f"Content was substantially shaped by both human and AI contributions."
        )
    else:
        category = AttributionCategory.HUMAN_AUTHORED
        confidence = min(
            (edit_dist - _CO_CREATED_THRESHOLD)
            / (1.0 - _CO_CREATED_THRESHOLD)
            + 0.6,
            1.0,
        )
        evidence = (
            f"Edit distance {edit_dist:.1%} exceeds the {_CO_CREATED_THRESHOLD:.0%} "
            f"threshold. The final version diverges significantly from AI output, "
            f"indicating primary human authorship."
        )

    return category, round(confidence, 4), evidence


class AttributionTracker:
    """Tracks attribution records for all turns in a session.

    Maintains a registry of AI outputs and their corresponding final
    (human-approved) versions, computing attribution classifications
    based on edit distance analysis.
    """

    def __init__(self) -> None:
        self._records: dict[str, AttributionRecord] = {}
        self._ai_outputs: dict[str, str] = {}
        self._final_versions: dict[str, str] = {}

    def record_ai_output(self, turn_id: str, content: str) -> None:
        """Record the original AI-generated output for a turn."""
        self._ai_outputs[turn_id] = content

    def record_final_version(self, turn_id: str, content: str) -> None:
        """Record the final human-approved version for a turn.

        If an AI output was previously recorded for this turn, the
        attribution is automatically computed.
        """
        self._final_versions[turn_id] = content

        if turn_id in self._ai_outputs:
            category, confidence, evidence = classify_attribution(
                self._ai_outputs[turn_id], content
            )
            self._records[turn_id] = AttributionRecord(
                turn_id=turn_id,
                category=category,
                confidence=confidence,
                evidence=evidence,
            )

    def record_human_only(self, turn_id: str, content: str) -> None:
        """Record a turn that is entirely human-authored (no AI involvement)."""
        self._final_versions[turn_id] = content
        self._records[turn_id] = AttributionRecord(
            turn_id=turn_id,
            category=AttributionCategory.HUMAN_AUTHORED,
            confidence=1.0,
            evidence="Content created entirely by human with no AI involvement.",
        )

    def get_record(self, turn_id: str) -> AttributionRecord | None:
        """Retrieve the attribution record for a specific turn."""
        return self._records.get(turn_id)

    def all_records(self) -> list[AttributionRecord]:
        """Return all attribution records in insertion order."""
        return list(self._records.values())

    def edit_distances(self) -> dict[str, float]:
        """Return normalized edit distances for all turns that have both versions."""
        distances: dict[str, float] = {}
        for turn_id in self._ai_outputs:
            if turn_id in self._final_versions:
                distances[turn_id] = normalized_edit_distance(
                    self._ai_outputs[turn_id],
                    self._final_versions[turn_id],
                )
        return distances

    def to_dict(self) -> dict[str, Any]:
        return {
            "records": {k: v.to_dict() for k, v in self._records.items()},
            "ai_outputs": dict(self._ai_outputs),
            "final_versions": dict(self._final_versions),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AttributionTracker:
        tracker = cls()
        tracker._ai_outputs = dict(data.get("ai_outputs", {}))
        tracker._final_versions = dict(data.get("final_versions", {}))
        for key, rec_data in data.get("records", {}).items():
            tracker._records[key] = AttributionRecord.from_dict(rec_data)
        return tracker
