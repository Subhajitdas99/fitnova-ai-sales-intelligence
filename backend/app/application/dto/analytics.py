from pydantic import BaseModel, Field


class ExecutiveDashboardResponse(BaseModel):
    average_ai_quality_score: float
    average_close_probability: float
    total_calls: int
    calls_processed_today: int
    average_call_duration: float
    average_engagement: float
    sentiment_distribution: dict[str, int] = Field(default_factory=dict)
    outcome_distribution: dict[str, int] = Field(default_factory=dict)


class AdvisorPerformanceResponse(BaseModel):
    advisor_name: str
    calls_handled: int
    average_ai_score: float
    average_close_probability: float
    average_rapport: float
    average_objection_handling: float
    average_discovery_score: float
    average_compliance_score: float


class CoachingCardResponse(BaseModel):
    call_id: str
    customer_name: str
    advisor_name: str
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    priority_improvement: str
    manager_feedback: str
    practice_goal: str
    next_coaching_exercise: str


class TimeSeriesPoint(BaseModel):
    date: str
    value: float
    label: str | None = None


class FrequencyPoint(BaseModel):
    label: str
    value: int


class CategoryDistributionPoint(BaseModel):
    category: str
    score: float
    call_id: str
    advisor_name: str


class AnalyticsDashboardResponse(BaseModel):
    call_volume: list[TimeSeriesPoint] = Field(default_factory=list)
    sentiment_trend: list[TimeSeriesPoint] = Field(default_factory=list)
    close_probability_trend: list[TimeSeriesPoint] = Field(default_factory=list)
    issue_frequency: list[FrequencyPoint] = Field(default_factory=list)
    top_customer_concerns: list[FrequencyPoint] = Field(default_factory=list)
    category_score_distribution: list[CategoryDistributionPoint] = Field(
        default_factory=list
    )
    advisor_leaderboard: list[AdvisorPerformanceResponse] = Field(default_factory=list)
