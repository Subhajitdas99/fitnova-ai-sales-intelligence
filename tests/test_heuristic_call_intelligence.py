from backend.app.domain.entities.transcript import TranscriptSegment
from backend.app.domain.enums import CallOutcome
from backend.app.infrastructure.services.heuristic_call_intelligence_service import (
    HeuristicCallIntelligenceService,
)


def test_heuristic_intelligence_extracts_follow_up_signal() -> None:
    service = HeuristicCallIntelligenceService()
    transcript = [
        TranscriptSegment(
            speaker_label="Sales Rep",
            text="We can support a pilot and share the proposal tomorrow.",
            start_time=0.0,
            end_time=5.0,
            confidence=0.99,
        ),
        TranscriptSegment(
            speaker_label="Customer",
            text="Pricing and integration are my main concerns, but I will review the pilot with my director.",
            start_time=5.0,
            end_time=11.0,
            confidence=0.98,
        ),
    ]

    result = service.analyze(
        customer_name="Acme Health",
        sales_rep_name="Jordan Lee",
        transcript_segments=transcript,
        notes=None,
    )

    assert result.outcome == CallOutcome.FOLLOW_UP
    assert result.objection_count >= 1
    assert result.action_items
