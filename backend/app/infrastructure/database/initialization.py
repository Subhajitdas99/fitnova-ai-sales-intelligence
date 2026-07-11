from sqlalchemy import inspect, text

from backend.app.infrastructure.database.base import Base
from backend.app.infrastructure.database.models.action_item import ActionItemModel
from backend.app.infrastructure.database.models.call_record import CallRecordModel
from backend.app.infrastructure.database.models.scorecard_evidence import ScorecardEvidenceModel
from backend.app.infrastructure.database.models.transcript_segment import TranscriptSegmentModel
from backend.app.infrastructure.database.session import engine


def initialize_database() -> None:
    """Create database tables for local development and demo environments."""

    Base.metadata.create_all(bind=engine)
    _migrate_sqlite_transcript_speaker_column()
    _migrate_sqlite_call_analysis_columns()


def _migrate_sqlite_transcript_speaker_column() -> None:
    """Keep local SQLite databases compatible with the Sprint 4 transcript schema."""

    if engine.dialect.name != "sqlite":
        return

    inspector = inspect(engine)
    if "transcript_segments" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("transcript_segments")}
    if "speaker" in columns or "speaker_label" not in columns:
        return

    with engine.begin() as connection:
        connection.execute(
            text("ALTER TABLE transcript_segments RENAME COLUMN speaker_label TO speaker")
        )


def _migrate_sqlite_call_analysis_columns() -> None:
    """Add Sprint 5 analysis columns for local SQLite databases."""

    if engine.dialect.name != "sqlite":
        return

    inspector = inspect(engine)
    if "call_records" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("call_records")}
    column_statements = {
        "executive_summary": "ALTER TABLE call_records ADD COLUMN executive_summary TEXT",
        "overall_score": "ALTER TABLE call_records ADD COLUMN overall_score FLOAT",
        "overall_confidence": "ALTER TABLE call_records ADD COLUMN overall_confidence FLOAT",
        "category_scores": "ALTER TABLE call_records ADD COLUMN category_scores JSON NOT NULL DEFAULT '{}'",
        "category_score_details": "ALTER TABLE call_records ADD COLUMN category_score_details JSON NOT NULL DEFAULT '[]'",
        "detected_issues": "ALTER TABLE call_records ADD COLUMN detected_issues JSON NOT NULL DEFAULT '[]'",
        "coaching_recommendations": "ALTER TABLE call_records ADD COLUMN coaching_recommendations JSON NOT NULL DEFAULT '[]'",
    }

    with engine.begin() as connection:
        for column_name, statement in column_statements.items():
            if column_name not in columns:
                connection.execute(text(statement))
