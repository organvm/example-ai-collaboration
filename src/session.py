"""Collaboration session model for tracking AI-human interactions.

A session represents a complete collaboration between human participants
and AI models, organized as a sequence of turns with lifecycle management.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class SessionState(Enum):
    """Lifecycle states for a collaboration session."""

    OPEN = "OPEN"
    REVIEWING = "REVIEWING"
    CLOSED = "CLOSED"


class ContributorType(Enum):
    """Whether a turn contributor is human or AI."""

    HUMAN = "human"
    AI = "ai"


@dataclass
class Participant:
    """A session participant — either a human or an AI model."""

    name: str
    role: ContributorType
    model: str | None = None  # Only set for AI participants

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "name": self.name,
            "role": self.role.value,
        }
        if self.model is not None:
            result["model"] = self.model
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Participant:
        return cls(
            name=data["name"],
            role=ContributorType(data["role"]),
            model=data.get("model"),
        )


@dataclass
class Turn:
    """A single turn in the collaboration — one contribution from one participant."""

    id: str
    contributor: str  # Participant name
    contributor_type: ContributorType
    content: str
    timestamp: datetime
    parent_turn_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def word_count(self) -> int:
        """Count words in the turn content."""
        return len(self.content.split())

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "contributor": self.contributor,
            "contributor_type": self.contributor_type.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "parent_turn_id": self.parent_turn_id,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Turn:
        return cls(
            id=data["id"],
            contributor=data["contributor"],
            contributor_type=ContributorType(data["contributor_type"]),
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            parent_turn_id=data.get("parent_turn_id"),
            metadata=data.get("metadata", {}),
        )


# Valid state transitions
_VALID_TRANSITIONS: dict[SessionState, list[SessionState]] = {
    SessionState.OPEN: [SessionState.REVIEWING, SessionState.CLOSED],
    SessionState.REVIEWING: [SessionState.OPEN, SessionState.CLOSED],
    SessionState.CLOSED: [],
}


class CollaborationSession:
    """A collaboration session tracking turns between humans and AI models.

    Lifecycle: OPEN -> REVIEWING -> CLOSED
    Turns can only be added while the session is OPEN.
    """

    def __init__(
        self,
        title: str,
        participants: list[Participant] | None = None,
        session_id: str | None = None,
    ) -> None:
        self.id: str = session_id or str(uuid.uuid4())
        self.title: str = title
        self.participants: list[Participant] = participants or []
        self.turns: list[Turn] = []
        self.state: SessionState = SessionState.OPEN
        self.created_at: datetime = datetime.now(timezone.utc)
        self.closed_at: datetime | None = None

    def add_participant(self, participant: Participant) -> None:
        """Add a participant to the session."""
        self.participants.append(participant)

    def add_turn(
        self,
        contributor: str,
        contributor_type: ContributorType,
        content: str,
        parent_turn_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Turn:
        """Add a turn to the session. Session must be OPEN."""
        if self.state != SessionState.OPEN:
            raise ValueError(
                f"Cannot add turns to a session in state {self.state.value}. "
                f"Session must be OPEN."
            )

        # Validate contributor is a known participant
        known_names = {p.name for p in self.participants}
        if contributor not in known_names:
            raise ValueError(
                f"Unknown contributor '{contributor}'. "
                f"Known participants: {known_names}"
            )

        # Validate parent turn exists if specified
        if parent_turn_id is not None:
            turn_ids = {t.id for t in self.turns}
            if parent_turn_id not in turn_ids:
                raise ValueError(
                    f"Parent turn '{parent_turn_id}' does not exist."
                )

        turn = Turn(
            id=str(uuid.uuid4()),
            contributor=contributor,
            contributor_type=contributor_type,
            content=content,
            timestamp=datetime.now(timezone.utc),
            parent_turn_id=parent_turn_id,
            metadata=metadata or {},
        )
        self.turns.append(turn)
        return turn

    def transition_to(self, new_state: SessionState) -> None:
        """Transition the session to a new lifecycle state."""
        valid_targets = _VALID_TRANSITIONS.get(self.state, [])
        if new_state not in valid_targets:
            raise ValueError(
                f"Invalid transition: {self.state.value} -> {new_state.value}. "
                f"Valid transitions from {self.state.value}: "
                f"{[s.value for s in valid_targets]}"
            )
        self.state = new_state
        if new_state == SessionState.CLOSED:
            self.closed_at = datetime.now(timezone.utc)

    def total_turns(self) -> int:
        """Total number of turns in the session."""
        return len(self.turns)

    def total_word_count(self) -> int:
        """Total word count across all turns."""
        return sum(t.word_count() for t in self.turns)

    def duration_seconds(self) -> float | None:
        """Session duration in seconds, or None if still open."""
        if self.closed_at is None:
            if not self.turns:
                return None
            last_ts = max(t.timestamp for t in self.turns)
            return (last_ts - self.created_at).total_seconds()
        return (self.closed_at - self.created_at).total_seconds()

    def to_dict(self) -> dict[str, Any]:
        """Serialize the session to a dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "participants": [p.to_dict() for p in self.participants],
            "turns": [t.to_dict() for t in self.turns],
            "state": self.state.value,
            "created_at": self.created_at.isoformat(),
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CollaborationSession:
        """Deserialize a session from a dictionary."""
        participants = [Participant.from_dict(p) for p in data["participants"]]
        session = cls(
            title=data["title"],
            participants=participants,
            session_id=data["id"],
        )
        session.turns = [Turn.from_dict(t) for t in data["turns"]]
        session.state = SessionState(data["state"])
        session.created_at = datetime.fromisoformat(data["created_at"])
        session.closed_at = (
            datetime.fromisoformat(data["closed_at"])
            if data.get("closed_at")
            else None
        )
        return session
