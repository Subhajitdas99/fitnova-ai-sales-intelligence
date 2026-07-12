from backend.app.application.dto.diarization_result import DiarizationResult
from backend.app.domain.entities.transcript import TranscriptSegment


class TranscriptDiarizationMergeService:
    """Combines Whisper transcript timing with speaker diarization windows."""

    def merge(
        self,
        transcript_segments: list[TranscriptSegment],
        diarization_result: DiarizationResult,
    ) -> list[TranscriptSegment]:
        if not diarization_result.segments:
            return [
                TranscriptSegment(
                    speaker=segment.speaker,
                    text=segment.text,
                    start_time=segment.start_time,
                    end_time=segment.end_time,
                    confidence=segment.confidence,
                )
                for segment in transcript_segments
            ]

        merged_segments: list[TranscriptSegment] = []
        for transcript_segment in transcript_segments:
            speaker = self._find_best_speaker(transcript_segment, diarization_result)
            merged_segments.append(
                TranscriptSegment(
                    speaker=speaker,
                    text=transcript_segment.text,
                    start_time=transcript_segment.start_time,
                    end_time=transcript_segment.end_time,
                    confidence=transcript_segment.confidence,
                )
            )
        return merged_segments

    def _find_best_speaker(
        self,
        transcript_segment: TranscriptSegment,
        diarization_result: DiarizationResult,
    ) -> str:
        best_speaker = transcript_segment.speaker or "Unknown"
        best_overlap = 0.0
        transcript_duration = max(
            transcript_segment.end_time - transcript_segment.start_time,
            0.001,
        )

        for speaker_segment in diarization_result.segments:
            overlap_start = max(
                transcript_segment.start_time, speaker_segment.start_time
            )
            overlap_end = min(transcript_segment.end_time, speaker_segment.end_time)
            overlap = max(0.0, overlap_end - overlap_start)
            normalized_overlap = overlap / transcript_duration
            if normalized_overlap > best_overlap:
                best_overlap = normalized_overlap
                best_speaker = speaker_segment.speaker

        return best_speaker
