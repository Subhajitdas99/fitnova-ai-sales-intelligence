from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.infrastructure.database.base import Base


class ActionItemModel(Base):
    """Persisted action item extracted from a call."""

    __tablename__ = "action_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    call_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("call_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    owner: Mapped[str] = mapped_column(String(255), nullable=False)
    due_hint: Mapped[str | None] = mapped_column(String(255), nullable=True)
    priority: Mapped[str] = mapped_column(String(32), nullable=False, default="medium")

    call_record: Mapped["CallRecordModel"] = relationship(back_populates="action_items")
