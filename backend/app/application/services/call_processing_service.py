import logging
from pathlib import Path

from backend.app.application.interfaces.call_repository import CallRepositoryProtocol
from backend.app.application.interfaces.services import (
    CallIntelligenceServiceProtocol,
    DiarizationServiceProtocol,
    TranscriptionServiceProtocol,
)
from backend.app.application.services.transcript_merge_service import (
    TranscriptDiarizationMergeService,
)
from backend.app.core.exceptions import ApplicationError, ResourceNotFoundError
from backend.app.domain.enums import CallStatus

logger = logging.getLogger(__name__)


class CallProcessingService:
    """Orchestrates transcription, diarization, and insight generation."""

    def __init__(
        self,
        repository: CallRepositoryProtocol,
        transcription_service: TranscriptionServiceProtocol,
        diarization_service: DiarizationServiceProtocol,
        transcript_merge_service: TranscriptDiarizationMergeService,
        intelligence_service: CallIntelligenceServiceProtocol,
    ) -> None:
        self._repository = repository
        self._transcription_service = transcription_service
        self._diarization_service = diarization_service
        self._transcript_merge_service = transcript_merge_service
        self._intelligence_service = intelligence_service

    def process_call(self, call_id: str) -> None:
        record = self._repository.get_call(call_id)
        if record is None:
            raise ResourceNotFoundError(f"Call '{call_id}' was not found.")

        self._repository.update_status(call_id, CallStatus.PROCESSING)
        logger.info(
            "Processing call started",
            extra={"call_id": call_id, "pipeline_step": "started"},
        )

        try:
            audio_path = Path(record.audio_path)
            logger.info(
                "Processing call transcription started",
                extra={"call_id": call_id, "pipeline_step": "transcription_started"},
            )
            transcription_result = self._transcription_service.transcribe(
                audio_path=audio_path,
                language=record.language,
            )
            transcript_segments = transcription_result.segments
            duration_seconds = max(
                (segment.end_time for segment in transcript_segments), default=0.0
            )
            logger.info(
                "Processing call transcription completed",
                extra={
                    "call_id": call_id,
                    "pipeline_step": "transcription_completed",
                    "segment_count": len(transcript_segments),
                    "detected_language": transcription_result.detected_language,
                },
            )
            self._repository.save_transcript(
                call_id=call_id,
                transcript_segments=transcript_segments,
                language=transcription_result.detected_language,
                duration_seconds=duration_seconds or None,
            )

            logger.info(
                "Processing call diarization started",
                extra={"call_id": call_id, "pipeline_step": "diarization_started"},
            )
            diarization_result = self._diarization_service.diarize(
                audio_path=audio_path,
                transcript_segments=transcript_segments,
            )
            logger.info(
                "Processing call diarization completed",
                extra={
                    "call_id": call_id,
                    "pipeline_step": "diarization_completed",
                    "speaker_window_count": len(diarization_result.segments),
                    "provider": diarization_result.provider,
                },
            )
            diarized_segments = self._transcript_merge_service.merge(
                transcript_segments=transcript_segments,
                diarization_result=diarization_result,
            )
            duration_seconds = max(
                (segment.end_time for segment in diarized_segments), default=0.0
            )
            self._repository.save_transcript(
                call_id=call_id,
                transcript_segments=diarized_segments,
                language=transcription_result.detected_language,
                duration_seconds=duration_seconds or None,
            )

            logger.info(
                "Processing call intelligence analysis started",
                extra={"call_id": call_id, "pipeline_step": "analysis_started"},
            )
            analysis = self._intelligence_service.analyze(
                customer_name=record.customer_name,
                sales_rep_name=record.sales_rep_name,
                transcript_segments=diarized_segments,
                notes=record.notes,
            )
            analysis.transcript_segments = diarized_segments
            self._repository.save_analysis(
                call_id=call_id,
                analysis=analysis,
                duration_seconds=duration_seconds or None,
            )
            logger.info(
                "Processing call completed",
                extra={"call_id": call_id, "pipeline_step": "completed"},
            )
        except ApplicationError as exc:
            logger.exception(
                "Processing call failed with an application error",
                extra={"call_id": call_id, "pipeline_step": "failed"},
            )
            self._repository.update_status(call_id, CallStatus.FAILED, str(exc))
            raise
        except Exception as exc:
            logger.exception(
                "Processing call failed with an unexpected error",
                extra={"call_id": call_id, "pipeline_step": "failed"},
            )
            self._repository.update_status(call_id, CallStatus.FAILED, str(exc))
            raise
