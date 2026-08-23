from pydantic import BaseModel, Field


class Match(BaseModel):
    """Represents a mentor-mentee matching result."""

    mentor_id: str
    mentee_id: str

    # Overall compatibility
    score: float = Field(ge=0.0, le=1.0)

    # Individual scoring components
    skill_score: float = Field(default=0.0, ge=0.0, le=1.0)
    goal_score: float = Field(default=0.0, ge=0.0, le=1.0)
    expertise_score: float = Field(default=0.0, ge=0.0, le=1.0)
    experience_score: float = Field(default=0.0, ge=0.0, le=1.0)
    industry_score: float = Field(default=0.0, ge=0.0, le=1.0)
    availability_score: float = Field(default=0.0, ge=0.0, le=1.0)
    preference_score: float = Field(default=0.0, ge=0.0, le=1.0)

    # Matching status
    is_valid: bool = True

    # Explainability
    reasons: list[str] = Field(default_factory=list)
    constraint_violations: list[str] = Field(default_factory=list)
