import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.app.core.exceptions import ServiceConfigurationError
from backend.app.infrastructure.services.whisperx_diarization_service import (
    WhisperXDiarizationService,
)


class FakeDiarizationFrame:
    def to_dict(self, orientation: str) -> list[dict[str, object]]:
        assert orientation == "records"
        return [
            {"speaker": "SPEAKER_00", "start": 0.0, "end": 2.4},
            {"speaker": "SPEAKER_01", "start": 2.4, "end": 5.0},
        ]


class FakeDiarizationPipeline:
    def __init__(self, token: str, device: str) -> None:
        self.token = token
        self.device = device

    def __call__(self, audio: object) -> FakeDiarizationFrame:
        assert audio == "loaded-audio"
        return FakeDiarizationFrame()


def test_whisperx_diarization_returns_provider_neutral_result(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    audio_path = tmp_path / "call.wav"
    audio_path.write_bytes(b"audio")
    fake_whisperx = SimpleNamespace(
        load_audio=lambda path: "loaded-audio",
        DiarizationPipeline=FakeDiarizationPipeline,
    )
    monkeypatch.setitem(sys.modules, "whisperx", fake_whisperx)

    service = WhisperXDiarizationService(
        huggingface_auth_token="hf-token",
        device="cpu",
    )

    result = service.diarize(audio_path=audio_path)

    assert result.provider == "whisperx"
    assert [segment.speaker for segment in result.segments] == [
        "SPEAKER_00",
        "SPEAKER_01",
    ]
    assert result.segments[0].start_time == 0.0
    assert result.segments[1].end_time == 5.0


def test_whisperx_diarization_requires_huggingface_token(tmp_path: Path) -> None:
    audio_path = tmp_path / "call.wav"
    audio_path.write_bytes(b"audio")
    service = WhisperXDiarizationService(huggingface_auth_token=None)

    with pytest.raises(ServiceConfigurationError, match="HUGGINGFACE"):
        service.diarize(audio_path=audio_path)
