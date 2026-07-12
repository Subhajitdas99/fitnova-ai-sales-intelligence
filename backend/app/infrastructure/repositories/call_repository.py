from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.app.application.dto.call_context import CallCreationData
from backend.app.application.interfaces.call_repository import CallRepositoryProtocol
from backend.app.core.exceptions import ResourceNotFoundError
from backend.app.domain.entities.analysis import CallAnalysis
from backend.app.domain.entities.transcript import TranscriptSegment
from backend.app.domain.enums import CallStatus
from backend.app.infrastructure.database.models.action_item import ActionItemModel
from backend.app.infrastructure.database.models.call_record import CallRecordModel
from backend.app.infrastructure.database.models.scorecard_evidence import (
    ScorecardEvidenceModel,
)
from backend.app.infrastructure.database.models.transcript_segment import (
    TranscriptSegmentModel,
)


class CallRepository(CallRepositoryProtocol):
    """SQLAlchemy-backed repository for sales calls."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def create_call(self, data: CallCreationData) -> CallRecordModel:
        record = CallRecordModel(
            id=data.call_id,
            original_file_name=data.original_file_name,
            stored_file_name=data.stored_file_name,
            audio_path=data.audio_path,
            customer_name=data.customer_name,
            sales_rep_name=data.sales_rep_name,
            language=data.language,
            notes=data.notes,
            status=CallStatus.QUEUED.value,
        )
        self._db.add(record)
        self._db.commit()
        self._db.refresh(record)
        return record

    def get_call(self, call_id: str) -> CallRecordModel | None:
        statement = (
            select(CallRecordModel)
            .options(
                selectinload(CallRecordModel.transcript_segments),
                selectinload(CallRecordModel.action_items),
                selectinload(CallRecordModel.scorecard_evidence),
            )
            .where(CallRecordModel.id == call_id)
        )
        return self._db.scalar(statement)

    def list_calls(
        self,
        status: CallStatus | None = None,
        limit: int = 50,
    ) -> list[CallRecordModel]:
        statement = (
            select(CallRecordModel)
            .options(
                selectinload(CallRecordModel.transcript_segments),
                selectinload(CallRecordModel.action_items),
                selectinload(CallRecordModel.scorecard_evidence),
            )
            .order_by(CallRecordModel.created_at.desc())
            .limit(limit)
        )
        if status is not None:
            statement = statement.where(CallRecordModel.status == status.value)
        return list(self._db.scalars(statement).all())

    def list_calls_for_analytics(self) -> list[CallRecordModel]:
        statement = (
            select(CallRecordModel)
            .options(
                selectinload(CallRecordModel.transcript_segments),
                selectinload(CallRecordModel.action_items),
                selectinload(CallRecordModel.scorecard_evidence),
            )
            .order_by(CallRecordModel.created_at.asc())
        )
        return list(self._db.scalars(statement).all())

    def update_status(
        self,
        call_id: str,
        status: CallStatus,
        failure_reason: str | None = None,
    ) -> CallRecordModel:
        record = self.get_call(call_id)
        if record is None:
            raise ResourceNotFoundError(f"Call '{call_id}' was not found.")

        record.status = status.value
        record.failure_reason = failure_reason
        if status == CallStatus.COMPLETED:
            record.completed_at = datetime.now(timezone.utc)

        self._db.add(record)
        self._db.commit()
        self._db.refresh(record)
        return record

    def save_transcript(
        self,
        call_id: str,
        transcript_segments: list[TranscriptSegment],
        language: str | None = None,
        duration_seconds: float | None = None,
    ) -> CallRecordModel:
        record = self.get_call(call_id)
        if record is None:
            raise ResourceNotFoundError(f"Call '{call_id}' was not found.")

        if language:
            record.language = language
        record.duration_seconds = duration_seconds
        record.transcript_segments.clear()
        for segment in transcript_segments:
            record.transcript_segments.append(
                TranscriptSegmentModel(
                    speaker=segment.speaker,
                    text=segment.text,
                    start_time=segment.start_time,
                    end_time=segment.end_time,
                    confidence=segment.confidence,
                )
            )

        self._db.add(record)
        self._db.commit()
        self._db.refresh(record)
        return record

    def save_analysis(
        self,
        call_id: str,
        analysis: CallAnalysis,
        duration_seconds: float | None,
    ) -> CallRecordModel:
        record = self.get_call(call_id)
        if record is None:
            raise ResourceNotFoundError(f"Call '{call_id}' was not found.")

        record.summary = analysis.summary
        record.executive_summary = analysis.executive_summary or analysis.summary
        record.overall_score = analysis.overall_score
        record.overall_confidence = analysis.overall_confidence
        record.category_scores = analysis.category_scores
        record.category_score_details = analysis.category_score_details
        record.detected_issues = analysis.detected_issues
        record.coaching_recommendations = analysis.coaching_recommendations
        record.overall_sentiment = analysis.sentiment.value
        record.outcome = analysis.outcome.value
        record.coaching_notes = analysis.coaching_notes
        record.next_steps = analysis.next_steps
        record.objection_count = analysis.objection_count
        record.talk_ratio_rep = analysis.talk_ratio_rep
        record.talk_ratio_customer = analysis.talk_ratio_customer
        record.engagement_score = analysis.engagement_score
        record.close_probability = analysis.close_probability
        record.follow_up_required = analysis.follow_up_required
        record.detected_objections = analysis.detected_objections
        record.products_discussed = analysis.products_discussed
        record.key_topics = analysis.key_topics
        record.duration_seconds = duration_seconds
        record.status = CallStatus.COMPLETED.value
        record.completed_at = datetime.now(timezone.utc)
        record.failure_reason = None

        record.transcript_segments.clear()
        record.action_items.clear()
        record.scorecard_evidence.clear()
        for segment in analysis.transcript_segments:
            record.transcript_segments.append(
                TranscriptSegmentModel(
                    speaker=segment.speaker,
                    text=segment.text,
                    start_time=segment.start_time,
                    end_time=segment.end_time,
                    confidence=segment.confidence,
                )
            )
        for action_item in analysis.action_items:
            record.action_items.append(
                ActionItemModel(
                    description=action_item.description,
                    owner=action_item.owner,
                    due_hint=action_item.due_hint,
                    priority=action_item.priority,
                )
            )
        if analysis.scorecard is not None:
            record.scorecard_evidence.extend(
                self._build_scorecard_evidence_models(analysis.scorecard)
            )

        self._db.add(record)
        self._db.commit()
        self._db.refresh(record)
        return record

    def _build_scorecard_evidence_models(
        self, scorecard
    ) -> list[ScorecardEvidenceModel]:
        evidence_models: list[ScorecardEvidenceModel] = []
        for evidence in scorecard.evidence:
            evidence_models.append(
                ScorecardEvidenceModel(
                    score_name="overall",
                    score_type="overall",
                    score=scorecard.overall_score,
                    confidence=evidence.confidence,
                    evidence=evidence.evidence,
                    timestamp=evidence.timestamp,
                    speaker=evidence.speaker,
                    supporting_quote=evidence.supporting_quote,
                )
            )
        for category_score in scorecard.category_scores:
            for evidence in category_score.evidence:
                evidence_models.append(
                    ScorecardEvidenceModel(
                        score_name=category_score.category,
                        score_type="category",
                        score=category_score.score,
                        confidence=evidence.confidence,
                        evidence=evidence.evidence,
                        timestamp=evidence.timestamp,
                        speaker=evidence.speaker,
                        supporting_quote=evidence.supporting_quote,
                    )
                )
        return evidence_models
