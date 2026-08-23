"""
API request and response schemas for the mentor-matching endpoints.

These are intentionally separate from the engine's internal models so
that the API contract can evolve independently.
"""
from __future__ import annotations

from pydantic import BaseModel, Field

from matching_engine.models.mentor import Mentor
from matching_engine.models.mentee import Mentee


# ---------------------------------------------------------------------------
# Re-export engine models as the canonical input types
# The engine's Mentor / Mentee are already Pydantic v2 models so they work
# directly as FastAPI request body schemas.
# ---------------------------------------------------------------------------

MentorIn = Mentor
MenteeIn = Mentee


# ---------------------------------------------------------------------------
# Request bodies
# ---------------------------------------------------------------------------

class MatchRequest(BaseModel):
    """Request body for POST /match."""

    mentors: list[MentorIn] = Field(
        description="Pool of available mentors.",
        min_length=1,
    )
    mentees: list[MenteeIn] = Field(
        description="Pool of mentees seeking a match.",
        min_length=1,
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "mentors": [
                    {
                        "id": "m1",
                        "name": "Alice Chen",
                        "skills": ["python", "machine-learning"],
                        "expertise": ["mlops"],
                        "industry": "technology",
                        "years_experience": 10,
                        "experience_level": "senior",
                        "mentoring_topics": ["career-growth"],
                        "availability": ["weekday-evenings"],
                        "timezone": "PST",
                        "max_mentees": 2,
                    }
                ],
                "mentees": [
                    {
                        "id": "e1",
                        "name": "Bob Kim",
                        "skills": ["python"],
                        "skills_to_learn": ["machine-learning", "mlops"],
                        "industry": "technology",
                        "years_experience": 1,
                        "experience_level": "junior",
                        "availability": ["weekday-evenings"],
                        "timezone": "PST",
                    }
                ],
            }
        }
    }


class RecommendRequest(BaseModel):
    """Request body for POST /recommend."""

    mentors: list[MentorIn] = Field(
        description="Pool of available mentors.",
        min_length=1,
    )
    mentees: list[MenteeIn] = Field(
        description="Pool of mentees seeking recommendations.",
        min_length=1,
    )
    top_k: int = Field(
        default=3,
        ge=1,
        le=20,
        description="Maximum number of mentor recommendations to return per mentee.",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "mentors": [
                    {
                        "id": "m1",
                        "name": "Alice Chen",
                        "skills": ["python", "machine-learning"],
                        "expertise": ["mlops"],
                        "industry": "technology",
                        "years_experience": 10,
                        "experience_level": "senior",
                        "mentoring_topics": ["career-growth"],
                        "availability": ["weekday-evenings"],
                        "timezone": "PST",
                        "max_mentees": 2,
                    }
                ],
                "mentees": [
                    {
                        "id": "e1",
                        "name": "Bob Kim",
                        "skills": ["python"],
                        "skills_to_learn": ["machine-learning", "mlops"],
                        "industry": "technology",
                        "years_experience": 1,
                        "experience_level": "junior",
                        "availability": ["weekday-evenings"],
                        "timezone": "PST",
                    }
                ],
                "top_k": 3,
            }
        }
    }


# ---------------------------------------------------------------------------
# Response bodies
# ---------------------------------------------------------------------------

class MatchOut(BaseModel):
    """A single mentor-mentee match result returned by the API."""

    mentor_id: str
    mentee_id: str

    score: float = Field(ge=0.0, le=1.0, description="Overall compatibility score")

    # Score components
    skill_score: float = Field(default=0.0, ge=0.0, le=1.0)
    goal_score: float = Field(default=0.0, ge=0.0, le=1.0)
    expertise_score: float = Field(default=0.0, ge=0.0, le=1.0)
    experience_score: float = Field(default=0.0, ge=0.0, le=1.0)
    industry_score: float = Field(default=0.0, ge=0.0, le=1.0)
    availability_score: float = Field(default=0.0, ge=0.0, le=1.0)
    preference_score: float = Field(default=0.0, ge=0.0, le=1.0)

    is_valid: bool = True
    reasons: list[str] = Field(default_factory=list)
    constraint_violations: list[str] = Field(default_factory=list)


class MatchListResponse(BaseModel):
    """Response for POST /match."""

    matches: list[MatchOut]
    total: int = Field(description="Number of matches returned.")

    @classmethod
    def from_matches(cls, matches: list) -> "MatchListResponse":
        return cls(
            matches=[MatchOut(**m.model_dump()) for m in matches],
            total=len(matches),
        )


class RecommendResponse(BaseModel):
    """Response for POST /recommend."""

    recommendations: dict[str, list[MatchOut]] = Field(
        description="Maps each mentee id to their ranked list of mentor recommendations."
    )
    top_k: int
    mentee_count: int = Field(description="Number of mentees that received recommendations.")

    @classmethod
    def from_recommendations(
        cls,
        recommendations: dict,
        top_k: int,
    ) -> "RecommendResponse":
        return cls(
            recommendations={
                mentee_id: [MatchOut(**m.model_dump()) for m in matches]
                for mentee_id, matches in recommendations.items()
            },
            top_k=top_k,
            mentee_count=len(recommendations),
        )

