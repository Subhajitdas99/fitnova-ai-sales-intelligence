from __future__ import annotations

from typing import Protocol

from backend.app.application.dto.call_context import CallCreationData
from backend.app.domain.entities.analysis import CallAnalysis
from backend.app.domain.entities.transcript import TranscriptSegment
from backend.app.domain.enums import CallStatus
from backend.app.infrastructure.database.models.call_record import CallRecordModel


class CallRepositoryProtocol(Protocol):
    """Repository contract for call persistence."""

    def create_call(self, data: CallCreationData) -> CallRecordModel: ...

    def get_call(self, call_id: str) -> CallRecordModel | None: ...

    def list_calls(
        self, status: CallStatus | None = None, limit: int = 50
    ) -> list[CallRecordModel]: ...

    def list_calls_for_analytics(self) -> list[CallRecordModel]: ...

    def update_status(
        self,
        call_id: str,
        status: CallStatus,
        failure_reason: str | None = None,
    ) -> CallRecordModel: ...

    def save_transcript(
        self,
        call_id: str,
        transcript_segments: list[TranscriptSegment],
        language: str | None = None,
        duration_seconds: float | None = None,
    ) -> CallRecordModel: ...

    def save_analysis(
        self,
        call_id: str,
        analysis: CallAnalysis,
        duration_seconds: float | None,
    ) -> CallRecordModel: ...
