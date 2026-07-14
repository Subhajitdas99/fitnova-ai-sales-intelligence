import logging
from json import JSONDecodeError

from openai import OpenAI
from pydantic import ValidationError

from backend.app.application.dto.analysis_response import LLMAnalysisResponse
from backend.app.application.interfaces.services import CallIntelligenceServiceProtocol
from backend.app.application.services.prompt_builder import PromptBuilder
from backend.app.core.exceptions import ExternalServiceError, ServiceConfigurationError
from backend.app.domain.entities.analysis import ActionItem, CallAnalysis
from backend.app.domain.entities.transcript import TranscriptSegment

logger = logging.getLogger(__name__)


class OpenRouterCallIntelligenceService(CallIntelligenceServiceProtocol):
    """LLM-backed sales-call analysis through OpenRouter."""

    _max_invalid_json_attempts = 3

    def __init__(
        self,
        api_key: str | None,
        model: str,
        prompt_builder: PromptBuilder,
        client: OpenAI | None = None,
    ) -> None:
        if not api_key and client is None:
            raise ServiceConfigurationError(
                "OPENROUTER_API_KEY is required when analysis_provider=openrouter."
            )
        self._client = client or OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
        )
        self._model = model
        self._prompt_builder = prompt_builder

    def analyze(
        self,
        customer_name: str,
        sales_rep_name: str,
        transcript_segments: list[TranscriptSegment],
        notes: str | None = None,
    ) -> CallAnalysis:
        prompt = self._prompt_builder.build_sales_call_analysis_prompt(
            customer_name=customer_name,
            sales_rep_name=sales_rep_name,
            transcript_segments=transcript_segments,
            notes=notes,
        )

        last_validation_error: Exception | None = None
        for attempt in range(1, self._max_invalid_json_attempts + 1):
            content = self._request_analysis(prompt=prompt, attempt=attempt)
            try:
                response = LLMAnalysisResponse.model_validate_json(content)
                return self._to_call_analysis(
                    response=response,
                    transcript_segments=transcript_segments,
                )
            except (ValidationError, ValueError, JSONDecodeError) as exc:
                last_validation_error = exc
                logger.warning(
                    "OpenRouter returned invalid analysis JSON on attempt %s/%s: %s",
                    attempt,
                    self._max_invalid_json_attempts,
                    exc,
                )
                prompt = self._build_retry_prompt(prompt, content, exc)

        raise ExternalServiceError(
            "OpenRouter analysis returned invalid JSON after "
            f"{self._max_invalid_json_attempts} attempts: {last_validation_error}"
        )

    def _request_analysis(self, prompt: str, attempt: int) -> str:
        """Send the prompt to OpenRouter and return the JSON response."""
        try:  # pragma: no cover - network dependency
            response = self._client.chat.completions.create(
                model=self._model,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert AI sales coach.\n"
                            "Return ONLY one valid JSON object matching the required schema.\n"
                            "Do NOT include markdown.\n"
                            "Do NOT include explanations.\n"
                            "Do NOT wrap the JSON inside code fences."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0.1,
                max_tokens=6000,
            )
        except Exception as exc:  # pragma: no cover - network dependency
            raise ExternalServiceError(f"OpenRouter analysis failed: {exc}") from exc

        if not response.choices:
            raise ExternalServiceError("OpenRouter returned no completion choices.")

        content = response.choices[0].message.content
        if not content:
            raise ExternalServiceError("OpenRouter returned an empty response.")

        logger.info(
            "OpenRouter analysis response received on attempt %s",
            attempt,
        )
        return content

    def _build_retry_prompt(
        self,
        original_prompt: str,
        invalid_content: str,
        error: Exception,
    ) -> str:
        """Build a retry prompt after invalid JSON."""
        return (
            f"{original_prompt}\n\n"
            "Your previous response was rejected because it was not valid JSON "
            "for the required schema.\n"
            f"Validation error: {error}\n"
            f"Rejected response: {invalid_content[:2000]}\n"
            "Return one corrected JSON object only."
        )

    def _to_call_analysis(
        self,
        response: LLMAnalysisResponse,
        transcript_segments: list[TranscriptSegment],
    ) -> CallAnalysis:
        talk_ratio_rep, talk_ratio_customer = self._calculate_talk_ratios(
            transcript_segments
        )
        coaching_notes = "\n".join(response.coaching_recommendations)
        category_score_details = [
            category_score.model_dump()
            for category_score in response.scorecard.category_scores
        ]
        category_scores = {
            category_score.category: category_score.score
            for category_score in response.scorecard.category_scores
        }
        return CallAnalysis(
            summary=response.executive_summary,
            executive_summary=response.executive_summary,
            overall_score=response.scorecard.overall_score,
            overall_confidence=response.scorecard.confidence,
            category_scores=category_scores,
            category_score_details=category_score_details,
            scorecard=response.scorecard,
            detected_issues=response.detected_issues,
            coaching_recommendations=response.coaching_recommendations,
            sentiment=response.sentiment,
            outcome=response.outcome,
            coaching_notes=coaching_notes,
            next_steps=response.next_steps,
            objection_count=len(response.detected_objections),
            talk_ratio_rep=talk_ratio_rep,
            talk_ratio_customer=talk_ratio_customer,
            engagement_score=response.scorecard.overall_score,
            close_probability=response.scorecard.overall_score,
            follow_up_required=response.follow_up_required,
            detected_objections=response.detected_objections,
            products_discussed=response.products_discussed,
            key_topics=response.key_topics,
            action_items=[
                ActionItem(
                    description=item.description,
                    owner=item.owner,
                    due_hint=item.due_hint,
                    priority=item.priority,
                )
                for item in response.action_items
            ],
            transcript_segments=transcript_segments,
        )

    def _calculate_talk_ratios(
        self,
        transcript_segments: list[TranscriptSegment],
    ) -> tuple[float, float]:
        rep_talk_time = sum(
            segment.end_time - segment.start_time
            for segment in transcript_segments
            if segment.speaker == "Sales Rep"
        )
        customer_talk_time = sum(
            segment.end_time - segment.start_time
            for segment in transcript_segments
            if segment.speaker != "Sales Rep"
        )
        total_talk_time = max(rep_talk_time + customer_talk_time, 1.0)
        return (
            round(rep_talk_time / total_talk_time, 2),
            round(customer_talk_time / total_talk_time, 2),
        )
