from pydantic import BaseModel, Field


class Mentee(BaseModel):
    """Represents a mentee looking for a mentor."""

    id: str

    name: str

    # Current profile
    skills: list[str] = Field(default_factory=list)
    experience_level: str | None = None
    years_experience: int = Field(default=0, ge=0)
    industry: str | None = None

    # What the mentee wants to achieve
    goals: list[str] = Field(default_factory=list)
    skills_to_learn: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)

    # Availability
    availability: list[str] = Field(default_factory=list)
    timezone: str | None = None

    # Preferences
    preferred_industries: list[str] = Field(default_factory=list)
    preferred_mentor_experience_levels: list[str] = Field(
        default_factory=list
    )
    preferred_mentor_topics: list[str] = Field(
        default_factory=list
    )
