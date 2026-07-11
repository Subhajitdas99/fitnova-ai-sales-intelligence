import logging
import math
import shutil
from pathlib import Path
from threading import Lock
from typing import Any

from tenacity import (
    Retrying,
    before_sleep_log,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
)

from backend.app.application.dto.transcription_result import TranscriptionResult
from backend.app.application.interfaces.services import TranscriptionServiceProtocol
from backend.app.core.exceptions import ApplicationError, ExternalServiceError, ServiceConfigurationError
from backend.app.domain.entities.transcript import TranscriptSegment


class WhisperTranscriptionService(TranscriptionServiceProtocol):
    """Local Whisper transcription adapter."""

    _supported_extensions = {".mp3", ".wav", ".m4a", ".mp4", ".mpeg", ".ogg"}

    def __init__(
        self,
        model_size: str,
        device: str = "auto",
        retry_attempts: int = 3,
        retry_delay_seconds: float = 2.0,
        temperature: float = 0.0,
    ) -> None:
        self._model_size = model_size
        self._device = device
        self._retry_attempts = retry_attempts
        self._retry_delay_seconds = retry_delay_seconds
        self._temperature = temperature
        self._model: Any | None = None
        self._resolved_device: str | None = None
        self._model_lock = Lock()
        self._logger = logging.getLogger(__name__)

    def transcribe(self, audio_path: Path, language: str | None = None) -> TranscriptionResult:
        resolved_audio_path = audio_path.expanduser().resolve()
        normalized_language = self._normalize_language(language)
        self._logger.info(
            "Whisper transcription started for %s (language hint: %s)",
            resolved_audio_path,
            normalized_language or "auto",
        )
        self._validate_audio_path(resolved_audio_path)

        result = self._transcribe_with_retry(
            audio_path=resolved_audio_path,
            language=normalized_language,
        )
        segments = self._build_segments(result)
        if not segments:
            raise ExternalServiceError(
                f"Whisper returned no transcript segments for '{resolved_audio_path.name}'."
            )

        detected_language = str(result.get("language") or normalized_language or "unknown").lower()
        average_confidence = sum(segment.confidence for segment in segments) / len(segments)
        self._logger.info(
            "Whisper transcription completed for %s with %s segments, detected language '%s', average confidence %.4f",
            resolved_audio_path,
            len(segments),
            detected_language,
            average_confidence,
        )
        return TranscriptionResult(
            detected_language=detected_language,
            segments=segments,
        )

    def _transcribe_with_retry(self, audio_path: Path, language: str | None) -> dict[str, Any]:
        for attempt in Retrying(
            stop=stop_after_attempt(self._retry_attempts),
            wait=wait_fixed(self._retry_delay_seconds),
            retry=retry_if_exception_type(ExternalServiceError),
            before_sleep=before_sleep_log(self._logger, logging.WARNING),
            reraise=True,
        ):
            with attempt:
                return self._transcribe_once(
                    audio_path=audio_path,
                    language=language,
                    attempt_number=attempt.retry_state.attempt_number,
                )

        raise ExternalServiceError(f"Whisper transcription failed for '{audio_path.name}'.")

    def _transcribe_once(
        self,
        audio_path: Path,
        language: str | None,
        attempt_number: int,
    ) -> dict[str, Any]:
        model = self._get_model()
        options: dict[str, Any] = {
            "task": "transcribe",
            "verbose": False,
            "temperature": self._temperature,
            "fp16": self._resolved_device == "cuda",
        }
        if language:
            options["language"] = language

        try:
            self._logger.info(
                "Whisper transcription attempt %s/%s for %s",
                attempt_number,
                self._retry_attempts,
                audio_path,
            )
            return model.transcribe(str(audio_path), **options)
        except Exception as exc:  # pragma: no cover - runtime dependency
            raise ExternalServiceError(
                f"Whisper transcription failed for '{audio_path.name}': {exc}"
            ) from exc

    def _get_model(self) -> Any:
        try:
            import whisper
            import torch
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise ServiceConfigurationError(
                "The 'openai-whisper' package is not installed. Install it together with PyTorch to enable local transcription."
            ) from exc

        if self._model is not None:
            return self._model

        with self._model_lock:
            if self._model is None:
                resolved_device = self._resolve_device(torch)
                self._logger.info(
                    "Loading Whisper model '%s' on %s",
                    self._model_size,
                    resolved_device,
                )
                try:
                    self._model = whisper.load_model(self._model_size, device=resolved_device)
                except Exception as exc:  # pragma: no cover - runtime dependency
                    raise ServiceConfigurationError(
                        f"Unable to load Whisper model '{self._model_size}': {exc}"
                    ) from exc
                self._resolved_device = resolved_device

        return self._model

    def _validate_audio_path(self, audio_path: Path) -> None:
        if not audio_path.exists() or not audio_path.is_file():
            raise ApplicationError(f"Audio file '{audio_path}' does not exist.")
        if audio_path.suffix.lower() not in self._supported_extensions:
            raise ApplicationError(
                "Unsupported audio format for Whisper transcription. Supported formats include mp3, wav, and m4a."
            )
        if shutil.which("ffmpeg") is None:
            raise ServiceConfigurationError(
                "Whisper transcription requires ffmpeg to be installed and available on PATH."
            )

    def _resolve_device(self, torch_module: Any) -> str:
        if self._device != "auto":
            return self._device
        return "cuda" if torch_module.cuda.is_available() else "cpu"

    def _normalize_language(self, language: str | None) -> str | None:
        normalized = (language or "").strip().lower()
        if normalized in {"", "auto", "detect", "auto-detect"}:
            return None
        return normalized

    def _build_segments(self, result: dict[str, Any]) -> list[TranscriptSegment]:
        segments: list[TranscriptSegment] = []
        for segment in result.get("segments", []):
            text = str(segment.get("text", "")).strip()
            if not text:
                continue
            segments.append(
                TranscriptSegment(
                    speaker="Unknown",
                    text=text,
                    start_time=float(segment.get("start", 0.0)),
                    end_time=float(segment.get("end", 0.0)),
                    confidence=self._estimate_confidence(segment),
                )
            )
        return segments

    def _estimate_confidence(self, segment: dict[str, Any]) -> float:
        avg_logprob = segment.get("avg_logprob")
        if avg_logprob is None:
            return 0.0

        confidence = math.exp(float(avg_logprob))
        no_speech_prob = segment.get("no_speech_prob")
        if no_speech_prob is not None:
            confidence *= max(0.0, min(1.0, 1.0 - float(no_speech_prob)))
        return round(max(0.0, min(1.0, confidence)), 4)
