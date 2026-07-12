from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.infrastructure.database.base import Base


class ScorecardEvidenceModel(Base):
    """Persisted evidence supporting scorecard scores."""

    __tablename__ = "scorecard_evidence"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    call_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("call_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    score_name: Mapped[str] = mapped_column(String(128), nullable=False)
    score_type: Mapped[str] = mapped_column(String(32), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    evidence: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[float] = mapped_column(Float, nullable=False)
    speaker: Mapped[str] = mapped_column(String(128), nullable=False, default="Unknown")
    supporting_quote: Mapped[str] = mapped_column(Text, nullable=False)

    call_record: Mapped["CallRecordModel"] = relationship(back_populates="scorecard_evidence")
