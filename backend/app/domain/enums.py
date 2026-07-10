from enum import Enum


class CallStatus(str, Enum):
    UPLOADED = "uploaded"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class SalesSentiment(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    MIXED = "mixed"


class CallOutcome(str, Enum):
    WON = "won"
    FOLLOW_UP = "follow_up"
    LOST = "lost"
    NURTURING = "nurturing"
    UNKNOWN = "unknown"
