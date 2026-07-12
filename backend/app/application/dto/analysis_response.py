from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.app.application.dto.scorecard import Scorecard
from backend.app.domain.enums import CallOutcome, SalesSentiment


class AnalysisActionItemResponse(BaseModel):
    """Validated action item produced by an LLM analysis provider."""

    model_config = ConfigDict(extra="forbid")

    description: str
    owner: str
    due_hint: str | None = None
    priority: str = "medium"


class LLMAnalysisResponse(BaseModel):
    """Strict provider response shape for sales-call analysis."""

    model_config = ConfigDict(extra="forbid")

    executive_summary: str
    scorecard: Scorecard
    detected_issues: list[str]
    coaching_recommendations: list[str]
    sentiment: SalesSentiment
    outcome: CallOutcome
    next_steps: str
    follow_up_required: bool
    detected_objections: list[str] = Field(default_factory=list)
    products_discussed: list[str] = Field(default_factory=list)
    key_topics: list[str] = Field(default_factory=list)
    action_items: list[AnalysisActionItemResponse] = Field(default_factory=list)

    @field_validator("scorecard")
    @classmethod
    def validate_scorecard(cls, value: Scorecard) -> Scorecard:
        if not value.category_scores:
            raise ValueError(
                "scorecard.category_scores must include at least one category."
            )
        for category_score in value.category_scores:
            if not category_score.category.strip():
                raise ValueError("category score names cannot be blank.")
        return value
