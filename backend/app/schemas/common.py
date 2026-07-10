from pydantic import BaseModel, ConfigDict


class ApiMessage(BaseModel):
    """Generic message response."""

    message: str


class ErrorResponse(BaseModel):
    """Standard error payload."""

    detail: str


class ORMModel(BaseModel):
    """Shared ORM serialization settings."""

    model_config = ConfigDict(from_attributes=True)
