import math
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.app.core.exceptions import ServiceConfigurationError
from backend.app.infrastructure.services.whisper_transcription_service import (
    WhisperTranscriptionService,
)


class FakeWhisperModel:
    def __init__(self, responses: list[object]) -> None:
        self._responses = responses
        self.calls: list[dict[str, object]] = []

    def transcribe(self, audio_path: str, **kwargs: object) -> dict[str, object]:
        self.calls.append({"audio_path": audio_path, **kwargs})
        response = self._responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def install_fake_whisper_runtime(monkeypatch: pytest.MonkeyPatch, model: FakeWhisperModel) -> None:
    fake_whisper = SimpleNamespace(load_model=lambda model_size, device=None: model)
    fake_torch = SimpleNamespace(cuda=SimpleNamespace(is_available=lambda: False))
    monkeypatch.setitem(sys.modules, "whisper", fake_whisper)
    monkeypatch.setitem(sys.modules, "torch", fake_torch)


def create_audio_file(tmp_path: Path, suffix: str = ".wav") -> Path:
    audio_path = tmp_path / f"sample{suffix}"
    audio_path.write_bytes(b"fake-audio")
    return audio_path


def test_whisper_transcription_auto_detects_language_and_returns_confident_segments(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_model = FakeWhisperModel(
        responses=[
            {
                "language": "es",
                "segments": [
                    {
                        "text": " Hola equipo ",
                        "start": 0.0,
                        "end": 1.8,
                        "avg_logprob": -0.2,
                        "no_speech_prob": 0.1,
                    }
                ],
            }
        ]
    )
    install_fake_whisper_runtime(monkeypatch, fake_model)
    monkeypatch.setattr(
        "backend.app.infrastructure.services.whisper_transcription_service.shutil.which",
        lambda _: "ffmpeg",
    )
    audio_path = create_audio_file(tmp_path)

    service = WhisperTranscriptionService(
        model_size="base",
        retry_attempts=2,
        retry_delay_seconds=0,
    )

    result = service.transcribe(audio_path=audio_path, language="auto")

    assert result.detected_language == "es"
    assert len(result.segments) == 1
    assert result.segments[0].text == "Hola equipo"
    assert result.segments[0].start_time == 0.0
    assert result.segments[0].end_time == 1.8
    assert result.segments[0].confidence == pytest.approx(
        round(math.exp(-0.2) * 0.9, 4)
    )
    assert "language" not in fake_model.calls[0]
    assert fake_model.calls[0]["fp16"] is False


def test_whisper_transcription_retries_transient_failures(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_model = FakeWhisperModel(
        responses=[
            RuntimeError("temporary decode failure"),
            {
                "language": "en",
                "segments": [
                    {
                        "text": "Retry succeeded",
                        "start": 0.0,
                        "end": 1.0,
                        "avg_logprob": -0.1,
                    }
                ],
            },
        ]
    )
    install_fake_whisper_runtime(monkeypatch, fake_model)
    monkeypatch.setattr(
        "backend.app.infrastructure.services.whisper_transcription_service.shutil.which",
        lambda _: "ffmpeg",
    )
    audio_path = create_audio_file(tmp_path, ".mp3")

    service = WhisperTranscriptionService(
        model_size="base",
        retry_attempts=2,
        retry_delay_seconds=0,
    )

    result = service.transcribe(audio_path=audio_path, language="en")

    assert result.detected_language == "en"
    assert len(fake_model.calls) == 2
    assert fake_model.calls[0]["language"] == "en"
    assert fake_model.calls[1]["language"] == "en"


def test_whisper_transcription_requires_ffmpeg(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    audio_path = create_audio_file(tmp_path, ".m4a")
    monkeypatch.setattr(
        "backend.app.infrastructure.services.whisper_transcription_service.shutil.which",
        lambda _: None,
    )

    service = WhisperTranscriptionService(model_size="base")

    with pytest.raises(ServiceConfigurationError, match="ffmpeg"):
        service.transcribe(audio_path=audio_path, language="auto")
