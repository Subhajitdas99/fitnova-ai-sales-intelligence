from backend.app.infrastructure.database.base import Base
from backend.app.infrastructure.database.models.action_item import ActionItemModel
from backend.app.infrastructure.database.models.call_record import CallRecordModel
from backend.app.infrastructure.database.models.transcript_segment import TranscriptSegmentModel
from backend.app.infrastructure.database.session import engine


def initialize_database() -> None:
    """Create database tables for local development and demo environments."""

    Base.metadata.create_all(bind=engine)
