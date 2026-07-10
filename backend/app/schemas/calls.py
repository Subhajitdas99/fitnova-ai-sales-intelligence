from datetime import datetime

from pydantic import BaseModel, Field

from backend.app.domain.enums import CallOutcome, CallStatus, SalesSentiment
from backend.app.schemas.common import ORMModel


class TranscriptSegmentResponse(ORMModel):
    id: int | None = None
    speaker_label: str
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
