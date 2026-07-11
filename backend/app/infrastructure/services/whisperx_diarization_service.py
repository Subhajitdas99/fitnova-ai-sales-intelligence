from pathlib import Path
from typing import Any

from backend.app.application.dto.diarization_result import (
    DiarizationResult,
    DiarizationSpeakerSegment,
)
from backend.app.application.interfaces.services import DiarizationServiceProtocol
from backend.app.core.exceptions import ExternalServiceError, ServiceConfigurationError
from backend.app.domain.entities.transcript import TranscriptSegment


class WhisperXDiarizationService(DiarizationServiceProtocol):
    """WhisperX-based diarization adapter."""

    def __init__(self, huggingface_auth_token: str | None, device: str = "cpu") -> None:
        self._huggingface_auth_token = huggingface_auth_token
        self._device = device

    def diarize(
        self,
        audio_path: Path,
        transcript_segments: list[TranscriptSegment] | None = None,
    ) -> DiarizationResult:
        if not self._huggingface_auth_token:
            raise ServiceConfigurationError(
                "WhisperX diarization requires FITNOVA_HUGGINGFACE_AUTH_TOKEN."
            )

        try:
            import whisperx
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise ServiceConfigurationError(
                "The 'whisperx' package is not installed. Install it or switch to heuristic diarization."
            ) from exc

        try:  # pragma: no cover - runtime dependency
            audio = whisperx.load_audio(str(audio_path))
            diarization_pipeline = self._build_diarization_pipeline(
                whisperx_module=whisperx,
            )
            diarization_segments = diarization_pipeline(audio)
        except Exception as exc:  # pragma: no cover - runtime dependency
            raise ExternalServiceError(f"WhisperX diarization failed: {exc}") from exc

        return DiarizationResult(
            segments=[
                DiarizationSpeakerSegment(
                    speaker=str(row.get("speaker", "Unknown")),
                    start_time=float(row["start"]),
                    end_time=float(row["end"]),
                )
                for row in diarization_segments.to_dict("records")
            ],
            provider="whisperx",
        )

    def _build_diarization_pipeline(self, whisperx_module: Any) -> Any:
        pipeline = getattr(whisperx_module, "DiarizationPipeline", None)
        if pipeline is None:
            from whisperx.diarize import DiarizationPipeline as pipeline

        try:
            return pipeline(token=self._huggingface_auth_token, device=self._device)
        except TypeError:
            return pipeline(use_auth_token=self._huggingface_auth_token, device=self._device)
