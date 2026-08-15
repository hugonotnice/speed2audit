from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AuditStatus(str, Enum):
    INITIALIZING = "INITIALIZING"
    SCRAPING = "SCRAPING"
    PERSONA_REVIEW = "PERSONA_REVIEW"
    AUDITING = "AUDITING"
    COMPLETED_SUCCESS = "COMPLETED_SUCCESS"
    COMPLETED_TIMEOUT = "COMPLETED_TIMEOUT"
    COMPLETED_LIMIT_REACHED = "COMPLETED_LIMIT_REACHED"
    FAILED = "FAILED"


class PersonaProfile(BaseModel):
    full_name: str
    company_name: str | None = None
    role: str
    core_pain_point: str
    budget_range: str | None = None
    urgency_level: str = "High"
    extra_instructions: str | None = None


class MessageRole(str, Enum):
    SHOPPER = "SHOPPER"
    TARGET_SELLER = "TARGET_SELLER"
    SYSTEM = "SYSTEM"


class ConversationTurn(BaseModel):
    turn_index: int
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=get_utc_now)
    latency_seconds_since_last: float | None = None


class Scorecard(BaseModel):
    first_response_time_seconds: float
    total_duration_seconds: float
    total_turns: int
    clarity_score: float = Field(ge=0, le=10)
    objection_handling_score: float = Field(ge=0, le=10)
    proactivity_score: float = Field(ge=0, le=10)
    executive_summary: str
    key_strengths: list[str] = Field(default_factory=list)
    areas_for_improvement: list[str] = Field(default_factory=list)


class AuditSession(BaseModel):
    session_id: str
    website_url: str
    target_phone: str
    status: AuditStatus = AuditStatus.INITIALIZING
    persona: PersonaProfile | None = None
    created_at: datetime = Field(default_factory=get_utc_now)
    turns: list[ConversationTurn] = Field(default_factory=list)
    scorecard: Scorecard | None = None
