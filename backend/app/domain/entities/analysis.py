from dataclasses import dataclass, field

from backend.app.domain.enums import CallOutcome, SalesSentiment
from backend.app.domain.entities.transcript import TranscriptSegment


@dataclass(slots=True)
class ActionItem:
    """Represents a follow-up action extracted from the sales call."""

    description: str
    owner: str
    due_hint: str | None = None
    priority: str = "medium"


@dataclass(slots=True)
class CallAnalysis:
    """Aggregated business insights produced from a sales call."""

    summary: str
    sentiment: SalesSentiment
    outcome: CallOutcome
    coaching_notes: str
    next_steps: str
    objection_count: int
    talk_ratio_rep: float
    talk_ratio_customer: float
    engagement_score: float
    close_probability: float
    follow_up_required: bool
    detected_objections: list[str] = field(default_factory=list)
    products_discussed: list[str] = field(default_factory=list)
    key_topics: list[str] = field(default_factory=list)
    action_items: list[ActionItem] = field(default_factory=list)
    transcript_segments: list[TranscriptSegment] = field(default_factory=list)
