from pathlib import Path
from types import SimpleNamespace

from backend.app.application.dto.transcription_result import TranscriptionResult
from backend.app.application.services.call_processing_service import CallProcessingService
from backend.app.domain.entities.analysis import CallAnalysis
from backend.app.domain.entities.transcript import TranscriptSegment
from backend.app.domain.enums import CallOutcome, CallStatus, SalesSentiment


class FakeRepository:
    def __init__(self, audio_path: Path) -> None:
        self.record = SimpleNamespace(
            id="call-1",
            audio_path=str(audio_path),
            customer_name="Acme Health",
            sales_rep_name="Jordan Lee",
            language="auto",
            notes="Discovery call",
        )
        self.status_updates: list[tuple[CallStatus, str | None]] = []
        self.saved_transcripts: list[dict[str, object]] = []
        self.saved_analysis: dict[str, object] | None = None

    def get_call(self, call_id: str):
        if call_id == self.record.id:
            return self.record
        return None

    def update_status(
        self,
        call_id: str,
        status: CallStatus,
        failure_reason: str | None = None,
    ):
        self.status_updates.append((status, failure_reason))
        return self.record

    def save_transcript(
        self,
        call_id: str,
        transcript_segments: list[TranscriptSegment],
        language: str | None = None,
        duration_seconds: float | None = None,
    ):
        self.saved_transcripts.append(
            {
                "call_id": call_id,
                "segments": transcript_segments,
                "language": language,
                "duration_seconds": duration_seconds,
            }
        )
        return self.record

    def save_analysis(
        self,
        call_id: str,
        analysis: CallAnalysis,
        duration_seconds: float | None,
    ):
        self.saved_analysis = {
            "call_id": call_id,
            "analysis": analysis,
            "duration_seconds": duration_seconds,
        }
        return self.record


class FakeTranscriptionService:
    def transcribe(self, audio_path: Path, language: str | None = None) -> TranscriptionResult:
        return TranscriptionResult(
            detected_language="en",
            segments=[
                TranscriptSegment(
                    speaker_label="Unknown",
                    text="Initial transcript",
                    start_time=0.0,
                    end_time=3.5,
                    confidence=0.91,
                )
            ],
        )


class FakeDiarizationService:
    def assign_speakers(
        self,
        audio_path: Path,
        transcript_segments: list[TranscriptSegment],
    ) -> list[TranscriptSegment]:
        return [
            TranscriptSegment(
                speaker_label="Sales Rep",
                text=segment.text,
                start_time=segment.start_time,
                end_time=segment.end_time,
                confidence=segment.confidence,
            )
            for segment in transcript_segments
        ]


class FakeCallIntelligenceService:
    def analyze(
        self,
        customer_name: str,
        sales_rep_name: str,
        transcript_segments: list[TranscriptSegment],
        notes: str | None = None,
    ) -> CallAnalysis:
        return CallAnalysis(
            summary="Summary",
            sentiment=SalesSentiment.POSITIVE,
            outcome=CallOutcome.FOLLOW_UP,
            coaching_notes="Coaching",
            next_steps="Next steps",
            objection_count=1,
            talk_ratio_rep=0.55,
            talk_ratio_customer=0.45,
            engagement_score=0.82,
            close_probability=0.68,
            follow_up_required=True,
            transcript_segments=transcript_segments,
        )


def test_call_processing_service_persists_transcript_before_analysis(tmp_path: Path) -> None:
    audio_path = tmp_path / "call.wav"
    audio_path.write_bytes(b"audio")
    repository = FakeRepository(audio_path)
    service = CallProcessingService(
        repository=repository,
        transcription_service=FakeTranscriptionService(),
        diarization_service=FakeDiarizationService(),
        intelligence_service=FakeCallIntelligenceService(),
    )

    service.process_call("call-1")

    assert repository.status_updates == [(CallStatus.PROCESSING, None)]
    assert len(repository.saved_transcripts) == 2
    assert repository.saved_transcripts[0]["language"] == "en"
    assert repository.saved_transcripts[0]["duration_seconds"] == 3.5
    assert repository.saved_transcripts[0]["segments"][0].speaker_label == "Unknown"
    assert repository.saved_transcripts[1]["segments"][0].speaker_label == "Sales Rep"
    assert repository.saved_analysis is not None
    assert repository.saved_analysis["duration_seconds"] == 3.5
