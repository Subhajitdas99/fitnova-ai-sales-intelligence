from dataclasses import dataclass


@dataclass(slots=True)
class TranscriptSegment:
    """Represents a time-bounded transcript segment."""

    speaker: str
    text: str
    start_time: float
    end_time: float
    confidence: float

    @property
    def speaker_label(self) -> str:
        """Compatibility alias for older application code."""

        return self.speaker
