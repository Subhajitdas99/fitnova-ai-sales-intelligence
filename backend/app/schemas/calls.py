from datetime import datetime

from pydantic import BaseModel, Field

from backend.app.domain.enums import CallOutcome, CallStatus, SalesSentiment
from backend.app.schemas.common import ORMModel


class TranscriptSegmentResponse(ORMModel):
    id: int | None = None
    call_id: str | None = None
    speaker: str
    text: str
    start_time: float
    end_time: float
    confidence: float


class ActionItemResponse(ORMModel):
    id: int | None = None
    description: str
    owner: str
    due_hint: str | None = None
    priority: str


class EvidenceResponse(ORMModel):
    id: int | None = None
    evidence: str
    timestamp: float
    supporting_quote: str


class CategoryScoreResponse(BaseModel):
    category: str
    score: float
    confidence: float
    evidence: list[EvidenceResponse] = Field(default_factory=list)


class ScorecardResponse(BaseModel):
    overall_score: float
    confidence: float
    evidence: list[EvidenceResponse] = Field(default_factory=list)
    category_scores: list[CategoryScoreResponse] = Field(default_factory=list)


class CallListItemResponse(ORMModel):
    id: str
    original_file_name: str
    customer_name: str
    sales_rep_name: str
    language: str
    status: CallStatus
    duration_seconds: float | None = None
    overall_sentiment: SalesSentiment | None = None
    outcome: CallOutcome | None = None
    close_probability: float | None = None
    created_at: datetime
    completed_at: datetime | None = None


class CallDetailResponse(CallListItemResponse):
    notes: str | None = None
    summary: str | None = None
    executive_summary: str | None = None
    overall_score: float | None = None
    overall_confidence: float | None = None
    category_scores: dict[str, float] = Field(default_factory=dict)
    category_score_details: list[dict[str, object]] = Field(default_factory=list)
    scorecard: ScorecardResponse | None = None
    detected_issues: list[str] = Field(default_factory=list)
    coaching_recommendations: list[str] = Field(default_factory=list)
    coaching_notes: str | None = None
    next_steps: str | None = None
    objection_count: int
    talk_ratio_rep: float | None = None
    talk_ratio_customer: float | None = None
    engagement_score: float | None = None
    follow_up_required: bool
    detected_objections: list[str] = Field(default_factory=list)
    products_discussed: list[str] = Field(default_factory=list)
    key_topics: list[str] = Field(default_factory=list)
    failure_reason: str | None = None
    transcript_segments: list[TranscriptSegmentResponse] = Field(default_factory=list)
    action_items: list[ActionItemResponse] = Field(default_factory=list)


class UploadCallResponse(ORMModel):
    id: str
    status: CallStatus
    original_file_name: str
    message: str


class DashboardOverviewResponse(BaseModel):
    total_calls: int
    completed_calls: int
    failed_calls: int
    processing_calls: int
    average_close_probability: float
    average_engagement_score: float
    sentiment_breakdown: dict[str, int]
    outcome_breakdown: dict[str, int]
    recent_calls: list[CallListItemResponse]
