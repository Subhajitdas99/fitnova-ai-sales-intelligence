from __future__ import annotations

from pathlib import Path
from typing import BinaryIO, Protocol

from backend.app.application.dto.diarization_result import DiarizationResult
from backend.app.application.dto.transcription_result import TranscriptionResult
from backend.app.domain.entities.analysis import CallAnalysis
from backend.app.domain.entities.transcript import TranscriptSegment


class AudioStorageProtocol(Protocol):
    """Storage abstraction for uploaded audio files."""

    def save(self, source: BinaryIO, destination_name: str) -> Path: ...


class TranscriptionServiceProtocol(Protocol):
    """Transcription abstraction for converting audio to text."""

    def transcribe(
        self, audio_path: Path, language: str | None = None
    ) -> TranscriptionResult: ...


class DiarizationServiceProtocol(Protocol):
    """Speaker diarization abstraction."""

    def diarize(
        self,
        audio_path: Path,
        transcript_segments: list[TranscriptSegment] | None = None,
    ) -> DiarizationResult: ...


class CallIntelligenceServiceProtocol(Protocol):
    """Insight generation abstraction for sales-call analysis."""

    def analyze(
        self,
        customer_name: str,
        sales_rep_name: str,
        transcript_segments: list[TranscriptSegment],
        notes: str | None = None,
    ) -> CallAnalysis: ...
