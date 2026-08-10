from pydantic import BaseModel, Field


class Mentor(BaseModel):
    """Represents a mentor available for matching."""

    id: str

    name: str

    # Professional profile
    skills: list[str] = Field(default_factory=list)
    expertise: list[str] = Field(default_factory=list)
    industry: str | None = None
    years_experience: int = Field(default=0, ge=0)
    experience_level: str | None = None

    # Mentoring capabilities
    mentoring_topics: list[str] = Field(default_factory=list)

    # Availability
    availability: list[str] = Field(default_factory=list)
    timezone: str | None = None

    # Preferences
    preferred_mentee_experience_levels: list[str] = Field(
        default_factory=list
    )
    preferred_industries: list[str] = Field(default_factory=list)

    # Capacity
    max_mentees: int = Field(default=1, ge=1)
    current_mentees: int = Field(default=0, ge=0)

    @property
    def available_capacity(self) -> int:
        """Return the number of additional mentees this mentor can accept."""
        return max(self.max_mentees - self.current_mentees, 0)
