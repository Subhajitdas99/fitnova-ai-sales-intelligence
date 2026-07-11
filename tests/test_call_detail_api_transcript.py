from datetime import datetime, timezone
from types import SimpleNamespace

from fastapi.testclient import TestClient

from backend.app.api.dependencies.services import get_call_repository
from backend.app.domain.enums import CallStatus
from backend.main import app


class FakeCallRepository:
    def get_call(self, call_id: str):
        if call_id != "call-1":
            return None
        return SimpleNamespace(
            id="call-1",
            original_file_name="call.wav",
            customer_name="Acme",
            sales_rep_name="Jordan",
            language="en",
            status=CallStatus.COMPLETED.value,
            duration_seconds=3.0,
            overall_sentiment=None,
            outcome=None,
            close_probability=None,
            created_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
            notes=None,
            summary="Summary",
            coaching_notes="Coaching",
            next_steps="Next",
            executive_summary="Executive summary",
            overall_score=88,
            overall_confidence=0.92,
            category_scores={"discovery": 90},
            category_score_details=[
                {"category": "discovery", "score": 90, "confidence": 0.87}
            ],
            scorecard={
                "overall_score": 88,
                "confidence": 0.92,
                "evidence": [
                    {
                        "id": 1,
                        "evidence": "Strong close.",
                        "timestamp": 2.2,
                        "supporting_quote": "I will send the proposal.",
                    }
                ],
                "category_scores": [
                    {
                        "category": "discovery",
                        "score": 90,
                        "confidence": 0.87,
                        "evidence": [
                            {
                                "id": 2,
                                "evidence": "Need was identified.",
                                "timestamp": 1.0,
                                "supporting_quote": "We need onboarding support.",
                            }
                        ],
                    }
                ],
            },
            objection_count=0,
            talk_ratio_rep=None,
            talk_ratio_customer=None,
            engagement_score=None,
            follow_up_required=True,
            detected_objections=[],
            products_discussed=[],
            key_topics=[],
            failure_reason=None,
            transcript_segments=[
                SimpleNamespace(
                    id=1,
                    call_id="call-1",
                    speaker="Sales Rep",
                    text="Hello",
                    start_time=0.0,
                    end_time=1.4,
                    confidence=0.9,
                ),
                SimpleNamespace(
                    id=2,
                    call_id="call-1",
                    speaker="Customer",
                    text="Hi",
                    start_time=1.4,
                    end_time=3.0,
                    confidence=0.88,
                ),
            ],
            action_items=[],
        )


def test_get_call_detail_returns_speaker_labeled_transcript_segments() -> None:
    app.dependency_overrides[get_call_repository] = lambda: FakeCallRepository()
    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/calls/call-1")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["transcript_segments"][0]["speaker"] == "Sales Rep"
    assert payload["transcript_segments"][0]["call_id"] == "call-1"
    assert "speaker_label" not in payload["transcript_segments"][0]
    assert payload["scorecard"]["confidence"] == 0.92
    assert payload["scorecard"]["category_scores"][0]["evidence"][0]["timestamp"] == 1.0
