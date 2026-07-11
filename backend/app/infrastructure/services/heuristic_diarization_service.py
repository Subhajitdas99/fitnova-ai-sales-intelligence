from pathlib import Path

from backend.app.application.dto.diarization_result import (
    DiarizationResult,
    DiarizationSpeakerSegment,
)
from backend.app.application.interfaces.services import DiarizationServiceProtocol
from backend.app.domain.entities.transcript import TranscriptSegment


class HeuristicDiarizationService(DiarizationServiceProtocol):
    """Assigns speakers using a simple alternating heuristic."""

    def diarize(
        self,
        audio_path: Path,
        transcript_segments: list[TranscriptSegment] | None = None,
    ) -> DiarizationResult:
        speaker_cycle = ("Sales Rep", "Customer")
        diarization_segments: list[DiarizationSpeakerSegment] = []
        for index, segment in enumerate(transcript_segments or []):
            diarization_segments.append(
                DiarizationSpeakerSegment(
                    speaker=speaker_cycle[index % 2],
                    start_time=segment.start_time,
                    end_time=segment.end_time,
                )
            )
        return DiarizationResult(
            segments=diarization_segments,
            provider="heuristic",
        )
