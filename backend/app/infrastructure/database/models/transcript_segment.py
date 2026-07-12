from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.infrastructure.database.base import Base


class TranscriptSegmentModel(Base):
    """Persisted transcript segment."""

    __tablename__ = "transcript_segments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    call_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("call_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    speaker: Mapped[str] = mapped_column(String(64), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    start_time: Mapped[float] = mapped_column(Float, nullable=False)
    end_time: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)

    call_record: Mapped["CallRecordModel"] = relationship(back_populates="transcript_segments")

    @property
    def speaker_label(self) -> str:
        """Compatibility alias for older callers."""

        return self.speaker
