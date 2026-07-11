from types import SimpleNamespace

from backend.app.application.services.prompt_builder import PromptBuilder
from backend.app.domain.entities.transcript import TranscriptSegment
from backend.app.domain.enums import CallOutcome, SalesSentiment
from backend.app.infrastructure.services.openrouter_call_intelligence_service import (
    OpenRouterCallIntelligenceService,
)


class FakeCompletions:
    def __init__(self, responses: list[str]) -> None:
        self._responses = responses
        self.calls: list[dict[str, object]] = []

    def create(self, **kwargs: object) -> SimpleNamespace:
        self.calls.append(kwargs)
        content = self._responses.pop(0)
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content=content),
                )
            ]
        )


class FakeOpenAIClient:
    def __init__(self, responses: list[str]) -> None:
        self.completions = FakeCompletions(responses)
        self.chat = SimpleNamespace(completions=self.completions)


def valid_response_json() -> str:
    return """
{
  "executive_summary": "The call showed strong interest with clear next steps.",
  "scorecard": {
    "overall_score": 82,
    "confidence": 0.91,
    "evidence": [
      {
        "evidence": "Customer showed interest in a pilot.",
        "timestamp": 0.8,
        "supporting_quote": "We can support your pilot."
      }
    ],
    "category_scores": [
      {
        "category": "discovery",
        "score": 80,
        "confidence": 0.88,
        "evidence": [
          {
            "evidence": "Rep identified a concrete pricing concern.",
            "timestamp": 3.2,
            "supporting_quote": "Pricing is my concern."
          }
        ]
      },
      {
        "category": "value_articulation",
        "score": 84,
        "confidence": 0.86,
        "evidence": [
          {
            "evidence": "Rep connected support to the pilot.",
            "timestamp": 0.3,
            "supporting_quote": "We can support your pilot."
          }
        ]
      }
    ]
  },
  "detected_issues": ["Pricing concern was not quantified."],
  "coaching_recommendations": ["Ask for budget range before presenting rollout options."],
  "sentiment": "positive",
  "outcome": "follow_up",
  "next_steps": "Send pilot proposal.",
  "follow_up_required": true,
  "detected_objections": ["Pricing"],
  "products_discussed": ["FitNova"],
  "key_topics": ["Pilot", "Pricing"],
  "action_items": [
    {
      "description": "Send pilot proposal.",
      "owner": "Jordan",
      "due_hint": "Tomorrow",
      "priority": "high"
    }
  ]
}
""".strip()


def transcript() -> list[TranscriptSegment]:
    return [
        TranscriptSegment(
            speaker="Sales Rep",
            text="We can support your pilot.",
            start_time=0.0,
            end_time=3.0,
            confidence=0.9,
        ),
        TranscriptSegment(
            speaker="Customer",
            text="Pricing is my concern.",
            start_time=3.0,
            end_time=5.0,
            confidence=0.9,
        ),
    ]


def test_openrouter_analysis_validates_response_and_maps_to_domain() -> None:
    client = FakeOpenAIClient([valid_response_json()])
    service = OpenRouterCallIntelligenceService(
        api_key=None,
        model="openai/gpt-4.1-mini",
        prompt_builder=PromptBuilder(),
        client=client,
    )

    analysis = service.analyze(
        customer_name="Acme",
        sales_rep_name="Jordan",
        transcript_segments=transcript(),
    )

    assert analysis.executive_summary.startswith("The call showed")
    assert analysis.summary == analysis.executive_summary
    assert analysis.overall_score == 82
    assert analysis.overall_confidence == 0.91
    assert analysis.category_scores["discovery"] == 80
    assert analysis.category_score_details[0]["confidence"] == 0.88
    assert analysis.scorecard is not None
    assert analysis.scorecard.evidence[0].supporting_quote == "We can support your pilot."
    assert analysis.detected_issues == ["Pricing concern was not quantified."]
    assert analysis.coaching_recommendations == [
        "Ask for budget range before presenting rollout options."
    ]
    assert analysis.sentiment == SalesSentiment.POSITIVE
    assert analysis.outcome == CallOutcome.FOLLOW_UP
    assert analysis.action_items[0].description == "Send pilot proposal."
    assert client.completions.calls[0]["response_format"] == {"type": "json_object"}


def test_openrouter_analysis_retries_invalid_json_responses() -> None:
    client = FakeOpenAIClient(["not json", valid_response_json()])
    service = OpenRouterCallIntelligenceService(
        api_key=None,
        model="openai/gpt-4.1-mini",
        prompt_builder=PromptBuilder(),
        client=client,
    )

    analysis = service.analyze(
        customer_name="Acme",
        sales_rep_name="Jordan",
        transcript_segments=transcript(),
    )

    assert analysis.overall_score == 82
    assert len(client.completions.calls) == 2
    retry_message = client.completions.calls[1]["messages"][1]["content"]
    assert "previous response was rejected" in retry_message
