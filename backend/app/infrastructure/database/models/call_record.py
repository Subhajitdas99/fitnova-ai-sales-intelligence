from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.infrastructure.database.base import Base


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""

    return datetime.now(timezone.utc)


class CallRecordModel(Base):
    """Persisted sales-call aggregate."""

    __tablename__ = "call_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    original_file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    audio_path: Mapped[str] = mapped_column(String(512), nullable=False)
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    sales_rep_name: Mapped[str] = mapped_column(String(255), nullable=False)
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="en")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="queued")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    overall_sentiment: Mapped[str | None] = mapped_column(String(32), nullable=True)
    outcome: Mapped[str | None] = mapped_column(String(32), nullable=True)
    executive_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    overall_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    overall_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    category_scores: Mapped[dict[str, float]] = mapped_column(JSON, nullable=False, default=dict)
    category_score_details: Mapped[list[dict[str, object]]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    detected_issues: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    coaching_recommendations: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    coaching_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    next_steps: Mapped[str | None] = mapped_column(Text, nullable=True)
    objection_count: Mapped[int] = mapped_column(nullable=False, default=0)
    talk_ratio_rep: Mapped[float | None] = mapped_column(Float, nullable=True)
    talk_ratio_customer: Mapped[float | None] = mapped_column(Float, nullable=True)
    engagement_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    close_probability: Mapped[float | None] = mapped_column(Float, nullable=True)
    follow_up_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    detected_objections: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    products_discussed: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    key_topics: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    transcript_segments: Mapped[list["TranscriptSegmentModel"]] = relationship(
        back_populates="call_record",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    action_items: Mapped[list["ActionItemModel"]] = relationship(
        back_populates="call_record",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    scorecard_evidence: Mapped[list["ScorecardEvidenceModel"]] = relationship(
        back_populates="call_record",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    @property
    def scorecard(self) -> dict[str, object] | None:
        """Return a nested API-friendly scorecard from persisted fields."""

        if self.overall_score is None:
            return None

        overall_evidence = [
            {
                "id": evidence.id,
                "evidence": evidence.evidence,
                "timestamp": evidence.timestamp,
                "speaker": evidence.speaker,
                "confidence": evidence.confidence,
                "supporting_quote": evidence.supporting_quote,
            }
            for evidence in self.scorecard_evidence
            if evidence.score_type == "overall"
        ]
        category_scores = []
        category_details = self.category_score_details or []
        for detail in category_details:
            category = str(detail.get("category", "Unknown"))
            category_scores.append(
                {
                    "category": category,
                    "score": float(detail.get("score", 0.0)),
                    "confidence": float(detail.get("confidence", 0.0)),
                    "evidence": [
                        {
                            "id": evidence.id,
                            "evidence": evidence.evidence,
                            "timestamp": evidence.timestamp,
                            "speaker": evidence.speaker,
                            "confidence": evidence.confidence,
                            "supporting_quote": evidence.supporting_quote,
                        }
                        for evidence in self.scorecard_evidence
                        if evidence.score_type == "category"
                        and evidence.score_name == category
                    ],
                }
            )

        return {
            "overall_score": self.overall_score,
            "confidence": self.overall_confidence or 0.0,
            "evidence": overall_evidence,
            "category_scores": category_scores,
        }
