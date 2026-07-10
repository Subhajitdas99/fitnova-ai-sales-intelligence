from dataclasses import dataclass, field

from backend.app.domain.entities.transcript import TranscriptSegment


@dataclass(slots=True)
class TranscriptionResult:
    """Structured output returned by transcription providers."""

    detected_language: str
    segments: list[TranscriptSegment] = field(default_factory=list)
