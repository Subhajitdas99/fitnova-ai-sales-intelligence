import json

from openai import OpenAI

from backend.app.application.interfaces.services import CallIntelligenceServiceProtocol
from backend.app.core.exceptions import ExternalServiceError, ServiceConfigurationError
from backend.app.domain.entities.analysis import ActionItem, CallAnalysis
from backend.app.domain.entities.transcript import TranscriptSegment
from backend.app.domain.enums import CallOutcome, SalesSentiment


class OpenAICallIntelligenceService(CallIntelligenceServiceProtocol):
    """LLM-backed sales-call analysis using the OpenAI API."""

    def __init__(self, api_key: str | None, model: str) -> None:
        if not api_key:
            raise ServiceConfigurationError(
                "FITNOVA_OPENAI_API_KEY is required when analysis_provider=openai."
            )
        self._client = OpenAI(api_key=api_key)
        self._model = model

    def analyze(
        self,
        customer_name: str,
        sales_rep_name: str,
        transcript_segments: list[TranscriptSegment],
        notes: str | None = None,
    ) -> CallAnalysis:
        transcript_text = "\n".join(
            f"{segment.speaker}: {segment.text}" for segment in transcript_segments
        )
        prompt = f"""
You are an expert sales call QA analyst.
Return valid JSON only with this schema:
{{
  "summary": "string",
  "sentiment": "positive|neutral|negative|mixed",
  "outcome": "won|follow_up|lost|nurturing|unknown",
  "coaching_notes": "string",
  "next_steps": "string",
  "objection_count": 0,
  "talk_ratio_rep": 0.0,
  "talk_ratio_customer": 0.0,
  "engagement_score": 0.0,
  "close_probability": 0.0,
  "follow_up_required": true,
  "detected_objections": ["string"],
  "products_discussed": ["string"],
  "key_topics": ["string"],
  "action_items": [
    {{
      "description": "string",
      "owner": "string",
      "due_hint": "string",
      "priority": "low|medium|high"
    }}
  ]
}}

Customer: {customer_name}
Sales rep: {sales_rep_name}
Additional notes: {notes or "None"}
Transcript:
{transcript_text}
""".strip()

        try:  # pragma: no cover - network dependency
            response = self._client.chat.completions.create(
                model=self._model,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": "You analyze B2B sales calls and return strict JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )
            content = response.choices[0].message.content or "{}"
            payload = json.loads(content)
        except Exception as exc:  # pragma: no cover - network dependency
            raise ExternalServiceError(f"OpenAI analysis failed: {exc}") from exc

        return CallAnalysis(
            summary=payload["summary"],
            sentiment=SalesSentiment(payload["sentiment"]),
            outcome=CallOutcome(payload["outcome"]),
            coaching_notes=payload["coaching_notes"],
            next_steps=payload["next_steps"],
            objection_count=int(payload["objection_count"]),
            talk_ratio_rep=float(payload["talk_ratio_rep"]),
            talk_ratio_customer=float(payload["talk_ratio_customer"]),
            engagement_score=float(payload["engagement_score"]),
            close_probability=float(payload["close_probability"]),
            follow_up_required=bool(payload["follow_up_required"]),
            detected_objections=list(payload.get("detected_objections", [])),
            products_discussed=list(payload.get("products_discussed", [])),
            key_topics=list(payload.get("key_topics", [])),
            action_items=[
                ActionItem(
                    description=item["description"],
                    owner=item["owner"],
                    due_hint=item.get("due_hint"),
                    priority=item.get("priority", "medium"),
                )
                for item in payload.get("action_items", [])
            ],
            transcript_segments=transcript_segments,
        )
