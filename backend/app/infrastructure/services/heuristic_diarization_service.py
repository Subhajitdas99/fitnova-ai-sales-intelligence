from pathlib import Path

from backend.app.application.interfaces.services import DiarizationServiceProtocol
from backend.app.domain.entities.transcript import TranscriptSegment


class HeuristicDiarizationService(DiarizationServiceProtocol):
    """Assigns speakers using a simple alternating heuristic."""

    def assign_speakers(
        self,
        audio_path: Path,
        transcript_segments: list[TranscriptSegment],
    ) -> list[TranscriptSegment]:
        speaker_cycle = ("Sales Rep", "Customer")
        diarized_segments: list[TranscriptSegment] = []
        for index, segment in enumerate(transcript_segments):
            diarized_segments.append(
                TranscriptSegment(
                    speaker_label=speaker_cycle[index % 2],
                    text=segment.text,
                    start_time=segment.start_time,
                    end_time=segment.end_time,
                    confidence=segment.confidence,
                )
            )
        return diarized_segments
