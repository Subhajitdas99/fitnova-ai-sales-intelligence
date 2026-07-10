from dataclasses import dataclass


@dataclass(slots=True)
class TranscriptSegment:
    """Represents a time-bounded transcript segment."""

    speaker_label: str
    text: str
    start_time: float
    end_time: float
    confidence: float
