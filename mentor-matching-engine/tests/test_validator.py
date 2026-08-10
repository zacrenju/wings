
from matching_engine.constraints.validator import (
    MatchingConstraintValidator,
)
from matching_engine.models import Mentor, Mentee


def test_valid_mentor_mentee_pair():
    mentor = Mentor(
        id="M001",
        name="Alice",
        skills=["Python", "Machine Learning"],
        expertise=["AI"],
        availability=["Saturday 10:00"],
        preferred_mentee_experience_levels=["beginner", "intermediate"],
        preferred_industries=["Aviation"],
        max_mentees=3,
        current_mentees=1,
    )

    mentee = Mentee(
        id="E001",
        name="Bob",
        skills=["Python"],
        experience_level="beginner",
        industry="Aviation",
        availability=["Saturday 10:00"],
        goals=["Learn Machine Learning"],
    )

    validator = MatchingConstraintValidator()

    result = validator.validate(mentor, mentee)

    assert result.is_valid is True
    assert result.violations == []


def test_mentor_without_capacity_is_invalid():
    mentor = Mentor(
        id="M001",
        name="Alice",
        max_mentees=2,
        current_mentees=2,
    )

    mentee = Mentee(
        id="E001",
        name="Bob",
    )

    validator = MatchingConstraintValidator()

    result = validator.validate(mentor, mentee)

    assert result.is_valid is False
    assert "no available capacity" in result.violations[0]


def test_no_availability_overlap_is_invalid():
    mentor = Mentor(
        id="M001",
        name="Alice",
        availability=["Saturday 10:00"],
    )

    mentee = Mentee(
        id="E001",
        name="Bob",
        availability=["Sunday 10:00"],
    )

    validator = MatchingConstraintValidator()

    result = validator.validate(mentor, mentee)

    assert result.is_valid is False
    assert any(
        "no overlapping availability" in violation
        for violation in result.violations
    )


def test_multiple_violations_are_returned():
    mentor = Mentor(
        id="M001",
        name="Alice",
        availability=["Saturday 10:00"],
        preferred_mentee_experience_levels=["senior"],
        preferred_industries=["Finance"],
        max_mentees=1,
        current_mentees=1,
    )

    mentee = Mentee(
        id="E001",
        name="Bob",
        experience_level="beginner",
        industry="Aviation",
        availability=["Sunday 10:00"],
    )

    validator = MatchingConstraintValidator()

    result = validator.validate(mentor, mentee)

    assert result.is_valid is False
    assert len(result.violations) == 4

