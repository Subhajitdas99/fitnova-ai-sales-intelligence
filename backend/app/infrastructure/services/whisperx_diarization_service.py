from pathlib import Path

from backend.app.application.interfaces.services import DiarizationServiceProtocol
from backend.app.core.exceptions import ExternalServiceError, ServiceConfigurationError
from backend.app.domain.entities.transcript import TranscriptSegment


class WhisperXDiarizationService(DiarizationServiceProtocol):
    """WhisperX-based diarization adapter."""

    def __init__(self, huggingface_auth_token: str | None) -> None:
        self._huggingface_auth_token = huggingface_auth_token

    def assign_speakers(
        self,
        audio_path: Path,
        transcript_segments: list[TranscriptSegment],
    ) -> list[TranscriptSegment]:
        try:
            import whisperx
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise ServiceConfigurationError(
                "The 'whisperx' package is not installed. Install it or switch to heuristic diarization."
            ) from exc

        if not self._huggingface_auth_token:
            raise ServiceConfigurationError(
                "WhisperX diarization requires FITNOVA_HUGGINGFACE_AUTH_TOKEN."
            )

        try:  # pragma: no cover - runtime dependency
            audio = whisperx.load_audio(str(audio_path))
            diarization_pipeline = whisperx.DiarizationPipeline(
                use_auth_token=self._huggingface_auth_token,
                device="cpu",
            )
            diarization_segments = diarization_pipeline(audio)
        except Exception as exc:  # pragma: no cover - runtime dependency
            raise ExternalServiceError(f"WhisperX diarization failed: {exc}") from exc

        assigned_segments: list[TranscriptSegment] = []
        diarization_rows = diarization_segments.to_dict("records")
        for index, segment in enumerate(transcript_segments):
            speaker_label = segment.speaker_label
            for diarization_segment in diarization_rows:
                if float(diarization_segment["start"]) <= segment.start_time <= float(
                    diarization_segment["end"]
                ):
                    speaker_label = str(diarization_segment.get("speaker", "Unknown"))
                    break
            assigned_segments.append(
                TranscriptSegment(
                    speaker_label=speaker_label,
                    text=segment.text,
                    start_time=segment.start_time,
                    end_time=segment.end_time,
                    confidence=segment.confidence,
                )
            )
        return assigned_segments
