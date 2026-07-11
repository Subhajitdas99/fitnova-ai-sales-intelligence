from dataclasses import dataclass, field


@dataclass(slots=True)
class DiarizationSpeakerSegment:
    """Provider-neutral speaker activity window."""

    speaker: str
    start_time: float
    end_time: float


@dataclass(slots=True)
class DiarizationResult:
    """Structured output returned by diarization providers."""

    segments: list[DiarizationSpeakerSegment] = field(default_factory=list)
    provider: str = "unknown"
