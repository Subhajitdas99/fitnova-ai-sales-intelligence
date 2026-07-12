from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.application.dto.call_context import CallCreationData
from backend.app.domain.entities.transcript import TranscriptSegment
from backend.app.infrastructure.database.base import Base
from backend.app.infrastructure.repositories.call_repository import CallRepository


def test_repository_persists_speaker_labeled_transcript_segments() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(
        bind=engine, autoflush=False, autocommit=False, future=True
    )

    with session_factory() as session:
        repository = CallRepository(session)
        repository.create_call(
            CallCreationData(
                call_id="call-1",
                original_file_name="call.wav",
                stored_file_name="call-1.wav",
                audio_path="/tmp/call.wav",
                customer_name="Acme",
                sales_rep_name="Jordan",
                language="en",
            )
        )

        repository.save_transcript(
            call_id="call-1",
            transcript_segments=[
                TranscriptSegment(
                    speaker="Sales Rep",
                    text="Hello",
                    start_time=0.0,
                    end_time=1.0,
                    confidence=0.95,
                ),
                TranscriptSegment(
                    speaker="Customer",
                    text="Hi",
                    start_time=1.0,
                    end_time=2.0,
                    confidence=0.9,
                ),
            ],
            language="en",
            duration_seconds=2.0,
        )

        record = repository.get_call("call-1")
        assert record is not None
        assert [segment.speaker for segment in record.transcript_segments] == [
            "Sales Rep",
            "Customer",
        ]
        assert record.transcript_segments[0].call_id == "call-1"
        assert record.duration_seconds == 2.0
