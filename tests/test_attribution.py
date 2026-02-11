"""Tests for the attribution model and edit-distance classification."""

from __future__ import annotations

import pytest

from src.attribution import (
    AttributionCategory,
    AttributionRecord,
    AttributionTracker,
    classify_attribution,
    normalized_edit_distance,
    _levenshtein_distance,
)


class TestLevenshteinDistance:
    def test_identical_strings(self) -> None:
        assert _levenshtein_distance("hello", "hello") == 0

    def test_empty_strings(self) -> None:
        assert _levenshtein_distance("", "") == 0

    def test_one_empty(self) -> None:
        assert _levenshtein_distance("abc", "") == 3
        assert _levenshtein_distance("", "abc") == 3

    def test_single_substitution(self) -> None:
        assert _levenshtein_distance("cat", "car") == 1

    def test_insertion_and_deletion(self) -> None:
        assert _levenshtein_distance("kitten", "sitting") == 3

    def test_completely_different(self) -> None:
        assert _levenshtein_distance("abc", "xyz") == 3


class TestNormalizedEditDistance:
    def test_identical_returns_zero(self) -> None:
        assert normalized_edit_distance("hello world", "hello world") == 0.0

    def test_completely_different_returns_high(self) -> None:
        dist = normalized_edit_distance("aaa", "zzz")
        assert dist == 1.0

    def test_empty_strings_return_zero(self) -> None:
        assert normalized_edit_distance("", "") == 0.0

    def test_partial_modification(self) -> None:
        dist = normalized_edit_distance("hello world", "hello earth")
        assert 0.0 < dist < 1.0


class TestClassifyAttribution:
    def test_identical_content_is_ai_generated(self) -> None:
        """If human accepts AI output verbatim, classify as AI_GENERATED."""
        original = "This is the AI-generated text about collaboration."
        category, confidence, evidence = classify_attribution(original, original)
        assert category == AttributionCategory.AI_GENERATED
        assert confidence == 1.0

    def test_minor_edit_is_ai_generated(self) -> None:
        """Small edits (< 10% change) still count as AI_GENERATED."""
        original = "This is a long piece of AI-generated content that covers many topics in depth."
        # Change just one word
        modified = "This is a long piece of AI-generated content that covers many topics in detail."
        category, _, _ = classify_attribution(original, modified)
        assert category == AttributionCategory.AI_GENERATED

    def test_moderate_edit_is_co_created(self) -> None:
        """Moderate edits (10-60%) count as CO_CREATED."""
        original = "The AI wrote this paragraph about technology and innovation."
        # Rewrite roughly half
        modified = "Technology and innovation are reshaping how we about technology and innovation."
        category, _, evidence = classify_attribution(original, modified)
        assert category == AttributionCategory.CO_CREATED
        assert "co-creation range" in evidence

    def test_major_rewrite_is_human_authored(self) -> None:
        """Heavy edits (> 60%) count as HUMAN_AUTHORED."""
        original = "Short AI text."
        modified = "A completely different and much longer piece written entirely by the human collaborator."
        category, _, evidence = classify_attribution(original, modified)
        assert category == AttributionCategory.HUMAN_AUTHORED
        assert "human authorship" in evidence.lower()


class TestAttributionRecord:
    def test_valid_confidence(self) -> None:
        record = AttributionRecord(
            turn_id="t1",
            category=AttributionCategory.CO_CREATED,
            confidence=0.85,
            evidence="Test evidence",
        )
        assert record.confidence == 0.85

    def test_invalid_confidence_raises(self) -> None:
        with pytest.raises(ValueError, match="between 0.0 and 1.0"):
            AttributionRecord(
                turn_id="t1",
                category=AttributionCategory.CO_CREATED,
                confidence=1.5,
                evidence="Invalid",
            )

    def test_serialization_roundtrip(self) -> None:
        record = AttributionRecord(
            turn_id="t1",
            category=AttributionCategory.AI_GENERATED,
            confidence=0.95,
            evidence="Accepted with minimal changes.",
        )
        data = record.to_dict()
        restored = AttributionRecord.from_dict(data)
        assert restored.turn_id == record.turn_id
        assert restored.category == record.category
        assert restored.confidence == record.confidence


class TestAttributionTracker:
    def test_record_human_only(self) -> None:
        tracker = AttributionTracker()
        tracker.record_human_only("t1", "Human content")
        record = tracker.get_record("t1")
        assert record is not None
        assert record.category == AttributionCategory.HUMAN_AUTHORED
        assert record.confidence == 1.0

    def test_record_ai_then_final(self) -> None:
        tracker = AttributionTracker()
        ai_text = "AI generated this response about the topic."
        tracker.record_ai_output("t1", ai_text)
        tracker.record_final_version("t1", ai_text)  # Accepted verbatim
        record = tracker.get_record("t1")
        assert record is not None
        assert record.category == AttributionCategory.AI_GENERATED

    def test_record_ai_then_heavily_edited(self) -> None:
        tracker = AttributionTracker()
        tracker.record_ai_output("t1", "Short text.")
        tracker.record_final_version(
            "t1",
            "A completely rewritten long piece that bears no resemblance to the original."
        )
        record = tracker.get_record("t1")
        assert record is not None
        assert record.category == AttributionCategory.HUMAN_AUTHORED

    def test_all_records(self) -> None:
        tracker = AttributionTracker()
        tracker.record_human_only("t1", "Human")
        tracker.record_ai_output("t2", "AI text")
        tracker.record_final_version("t2", "AI text")  # Accept verbatim
        records = tracker.all_records()
        assert len(records) == 2

    def test_edit_distances(self) -> None:
        tracker = AttributionTracker()
        tracker.record_ai_output("t1", "hello")
        tracker.record_final_version("t1", "hello")
        distances = tracker.edit_distances()
        assert distances["t1"] == 0.0

    def test_no_record_for_unknown_turn(self) -> None:
        tracker = AttributionTracker()
        assert tracker.get_record("nonexistent") is None

    def test_serialization_roundtrip(self) -> None:
        tracker = AttributionTracker()
        tracker.record_human_only("t1", "Human text")
        tracker.record_ai_output("t2", "AI draft")
        tracker.record_final_version("t2", "AI draft with edits by human reviewer")

        data = tracker.to_dict()
        restored = AttributionTracker.from_dict(data)
        assert len(restored.all_records()) == 2
