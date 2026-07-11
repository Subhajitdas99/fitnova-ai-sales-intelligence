from pydantic import BaseModel, ConfigDict, Field, model_validator


class Evidence(BaseModel):
    """Evidence supporting a scorecard judgment."""

    model_config = ConfigDict(extra="forbid")

    evidence: str
    timestamp: float = Field(ge=0.0)
    supporting_quote: str


class CategoryScore(BaseModel):
    """Per-category score with confidence and supporting evidence."""

    model_config = ConfigDict(extra="forbid")

    category: str
    score: float = Field(ge=0.0, le=100.0)
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[Evidence] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_evidence(self) -> "CategoryScore":
        if not self.evidence:
            raise ValueError("each category score must include at least one evidence item.")
        return self


class Scorecard(BaseModel):
    """Complete sales-call scorecard produced by an analysis provider."""

    model_config = ConfigDict(extra="forbid")

    overall_score: float = Field(ge=0.0, le=100.0)
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[Evidence] = Field(default_factory=list)
    category_scores: list[CategoryScore]

    @model_validator(mode="after")
    def require_scorecard_evidence(self) -> "Scorecard":
        if not self.evidence:
            raise ValueError("overall score must include at least one evidence item.")
        if not self.category_scores:
            raise ValueError("scorecard must include at least one category score.")
        return self
