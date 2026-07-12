from pathlib import Path

from backend.app.application.dto.transcription_result import TranscriptionResult
from backend.app.application.interfaces.services import TranscriptionServiceProtocol
from backend.app.domain.entities.transcript import TranscriptSegment


class MockTranscriptionService(TranscriptionServiceProtocol):
    """Deterministic transcript generator used for local demos and tests."""

    def transcribe(
        self, audio_path: Path, language: str | None = None
    ) -> TranscriptionResult:
        stem = audio_path.stem.replace("-", " ")
        return TranscriptionResult(
            detected_language=(language or "en"),
            segments=[
                TranscriptSegment(
                    speaker="Unknown",
                    text=f"Hi, thanks for joining. I wanted to walk you through the FitNova platform and how it could support your team. ({stem})",
                    start_time=0.0,
                    end_time=8.0,
                    confidence=0.98,
                ),
                TranscriptSegment(
                    speaker="Unknown",
                    text="We are evaluating solutions, but pricing and onboarding time are my biggest concerns right now.",
                    start_time=8.2,
                    end_time=16.5,
                    confidence=0.97,
                ),
                TranscriptSegment(
                    speaker="Unknown",
                    text="That makes sense. We typically start with a two-week rollout and provide a guided onboarding plan for every customer.",
                    start_time=16.8,
                    end_time=26.0,
                    confidence=0.98,
                ),
                TranscriptSegment(
                    speaker="Unknown",
                    text="Integration with our CRM is also important because our sales team does not want another disconnected tool.",
                    start_time=26.3,
                    end_time=35.6,
                    confidence=0.96,
                ),
                TranscriptSegment(
                    speaker="Unknown",
                    text="We already support API-based integrations and can map the workflow to your current CRM before rollout.",
                    start_time=36.0,
                    end_time=44.3,
                    confidence=0.97,
                ),
                TranscriptSegment(
                    speaker="Unknown",
                    text="If the proposal looks good, I can review it with my director next week and we can decide on a pilot.",
                    start_time=44.7,
                    end_time=53.5,
                    confidence=0.96,
                ),
            ],
        )
