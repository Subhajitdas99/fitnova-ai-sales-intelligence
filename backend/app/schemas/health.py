from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    database: str | None = None
    version: str


class ComponentHealth(BaseModel):
    status: str
    detail: str


class ReadinessResponse(BaseModel):
    status: str
    version: str
    checks: dict[str, ComponentHealth] = Field(default_factory=dict)
