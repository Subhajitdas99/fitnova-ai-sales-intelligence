from sqlalchemy import inspect, text

from backend.app.infrastructure.database.base import Base

# Imported for SQLAlchemy metadata registration.
from backend.app.infrastructure.database.models.action_item import (  # noqa: F401
    ActionItemModel,
)
from backend.app.infrastructure.database.models.call_record import (  # noqa: F401
    CallRecordModel,
)
from backend.app.infrastructure.database.models.scorecard_evidence import (  # noqa: F401
    ScorecardEvidenceModel,
)
from backend.app.infrastructure.database.models.transcript_segment import (  # noqa: F401
    TranscriptSegmentModel,
)
from backend.app.infrastructure.database.session import engine


def initialize_database() -> None:
    """
    Initialize the database and apply lightweight SQLite migrations.

    These migrations are intended only for local development/demo databases.
    Production environments should use Alembic.
    """
    Base.metadata.create_all(bind=engine)

    _migrate_sqlite_transcript_speaker_column()
    _migrate_sqlite_call_analysis_columns()
    _migrate_sqlite_scorecard_evidence_columns()


def _migrate_sqlite_transcript_speaker_column() -> None:
    """Rename speaker_label -> speaker for legacy SQLite databases."""

    if engine.dialect.name != "sqlite":
        return

    inspector = inspect(engine)

    if "transcript_segments" not in inspector.get_table_names():
        return

    columns = {
        column["name"] for column in inspector.get_columns("transcript_segments")
    }

    if "speaker" in columns or "speaker_label" not in columns:
        return

    with engine.begin() as connection:
        connection.execute(
            text(
                "ALTER TABLE transcript_segments "
                "RENAME COLUMN speaker_label TO speaker"
            )
        )


def _migrate_sqlite_call_analysis_columns() -> None:
    """Add Sprint 5 analysis columns to existing SQLite databases."""

    if engine.dialect.name != "sqlite":
        return

    inspector = inspect(engine)

    if "call_records" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("call_records")}

    column_statements = {
        "executive_summary": (
            "ALTER TABLE call_records " "ADD COLUMN executive_summary TEXT"
        ),
        "overall_score": ("ALTER TABLE call_records " "ADD COLUMN overall_score FLOAT"),
        "overall_confidence": (
            "ALTER TABLE call_records " "ADD COLUMN overall_confidence FLOAT"
        ),
        "category_scores": (
            "ALTER TABLE call_records "
            "ADD COLUMN category_scores JSON NOT NULL DEFAULT '{}'"
        ),
        "category_score_details": (
            "ALTER TABLE call_records "
            "ADD COLUMN category_score_details "
            "JSON NOT NULL DEFAULT '[]'"
        ),
        "detected_issues": (
            "ALTER TABLE call_records "
            "ADD COLUMN detected_issues "
            "JSON NOT NULL DEFAULT '[]'"
        ),
        "coaching_recommendations": (
            "ALTER TABLE call_records "
            "ADD COLUMN coaching_recommendations "
            "JSON NOT NULL DEFAULT '[]'"
        ),
    }

    with engine.begin() as connection:
        for column_name, statement in column_statements.items():
            if column_name not in columns:
                connection.execute(text(statement))


def _migrate_sqlite_scorecard_evidence_columns() -> None:
    """Add Sprint 7 evidence columns for legacy SQLite databases."""

    if engine.dialect.name != "sqlite":
        return

    inspector = inspect(engine)

    if "scorecard_evidence" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("scorecard_evidence")}

    column_statements = {
        "speaker": (
            "ALTER TABLE scorecard_evidence "
            "ADD COLUMN speaker VARCHAR(128) "
            "NOT NULL DEFAULT 'Unknown'"
        ),
        "confidence": (
            "ALTER TABLE scorecard_evidence "
            "ADD COLUMN confidence FLOAT "
            "NOT NULL DEFAULT 0.0"
        ),
    }

    with engine.begin() as connection:
        for column_name, statement in column_statements.items():
            if column_name not in columns:
                connection.execute(text(statement))
