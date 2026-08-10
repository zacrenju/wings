from matching_engine.models.mentor import Mentor
from matching_engine.models.mentee import Mentee
from matching_engine.optimization.candidate_generator import (
    CandidateGenerator,
)


def create_mentee(
    mentee_id: str = "e1",
    experience_level: str = "junior",
) -> Mentee:
    return Mentee(
        id=mentee_id,
        name="Alice",
        skills=["Python"],
        skills_to_learn=[
            "Python",
            "Machine Learning",
        ],
        goals=["Become an ML engineer"],
        interests=["AI"],
        industry="Aviation",
        years_experience=3,
        experience_level=experience_level,
        availability=["Monday", "Wednesday"],
        timezone="Asia/Kolkata",
    )


def create_mentor(
    mentor_id: str,
    skills: list[str],
    experience_level: str = "senior",
    current_mentees: int = 0,
    max_mentees: int = 1,
) -> Mentor:
    return Mentor(
        id=mentor_id,
        name=f"Mentor {mentor_id}",
        skills=skills,
        expertise=["Machine Learning"],
        industry="Aviation",
        years_experience=10,
        experience_level=experience_level,
        mentoring_topics=["Machine Learning"],
        availability=["Monday", "Wednesday"],
        timezone="Asia/Kolkata",
        max_mentees=max_mentees,
        current_mentees=current_mentees,
    )


def test_generates_candidates_for_mentee():
    mentors = [
        create_mentor(
            mentor_id="m1",
            skills=["Python", "Machine Learning"],
        ),
        create_mentor(
            mentor_id="m2",
            skills=["Python"],
        ),
    ]

    mentees = [create_mentee()]

    generator = CandidateGenerator()

    result = generator.generate(
        mentors,
        mentees,
    )

    assert "e1" in result
    assert len(result["e1"]) == 2


def test_candidates_are_ranked_by_score():
    """
    m2 is intentionally stronger than m1.

    m1:
        Python only

    m2:
        Python + Machine Learning
    """

    m1 = create_mentor(
        mentor_id="m1",
        skills=["Python"],
    )

    m1.expertise = ["Python"]
    m1.mentoring_topics = ["Python"]

    m2 = create_mentor(
        mentor_id="m2",
        skills=[
            "Python",
            "Machine Learning",
        ],
    )

    m2.expertise = [
        "Python",
        "Machine Learning",
    ]

    m2.mentoring_topics = [
        "Machine Learning",
    ]

    mentors = [m1, m2]
    mentees = [create_mentee()]

    generator = CandidateGenerator()

    result = generator.generate(
        mentors,
        mentees,
    )

    candidates = result["e1"]

    assert len(candidates) == 2

    # Candidates must be sorted highest score first.
    assert candidates[0].score >= candidates[1].score

    # m2 should be the stronger candidate.
    assert candidates[0].mentor_id == "m2"

    assert candidates[0].score > candidates[1].score


def test_multiple_mentees_get_candidates():
    mentors = [
        create_mentor(
            mentor_id="m1",
            skills=[
                "Python",
                "Machine Learning",
            ],
        ),
        create_mentor(
            mentor_id="m2",
            skills=["Python"],
        ),
    ]

    mentees = [
        create_mentee("e1"),
        create_mentee("e2"),
    ]

    generator = CandidateGenerator()

    result = generator.generate(
        mentors,
        mentees,
    )

    assert set(result.keys()) == {
        "e1",
        "e2",
    }

    assert len(result["e1"]) == 2
    assert len(result["e2"]) == 2


def test_mentor_without_capacity_is_excluded():
    mentors = [
        create_mentor(
            mentor_id="m1",
            skills=[
                "Python",
                "Machine Learning",
            ],
            max_mentees=1,
            current_mentees=1,
        ),
        create_mentor(
            mentor_id="m2",
            skills=["Python"],
        ),
    ]

    mentees = [create_mentee()]

    generator = CandidateGenerator()

    result = generator.generate(
        mentors,
        mentees,
    )

    candidates = result["e1"]

    assert len(candidates) == 1
    assert candidates[0].mentor_id == "m2"


def test_mentor_preferred_mentee_level_is_respected():
    mentor = create_mentor(
        mentor_id="m1",
        skills=[
            "Python",
            "Machine Learning",
        ],
    )

    mentor.preferred_mentee_experience_levels = [
        "mid",
        "senior",
    ]

    mentee = create_mentee(
        experience_level="junior",
    )

    generator = CandidateGenerator()

    result = generator.generate(
        [mentor],
        [mentee],
    )

    assert result["e1"] == []


def test_mentor_preferred_mentee_level_allows_match():
    mentor = create_mentor(
        mentor_id="m1",
        skills=[
            "Python",
            "Machine Learning",
        ],
    )

    mentor.preferred_mentee_experience_levels = [
        "junior",
        "mid",
    ]

    mentee = create_mentee(
        experience_level="junior",
    )

    generator = CandidateGenerator()

    result = generator.generate(
        [mentor],
        [mentee],
    )

    assert len(result["e1"]) == 1
    assert result["e1"][0].mentor_id == "m1"


def test_mentee_preferred_mentor_level_is_respected():
    mentor = create_mentor(
        mentor_id="m1",
        skills=[
            "Python",
            "Machine Learning",
        ],
        experience_level="junior",
    )

    mentee = create_mentee()

    mentee.preferred_mentor_experience_levels = [
        "senior",
    ]

    generator = CandidateGenerator()

    result = generator.generate(
        [mentor],
        [mentee],
    )

    assert result["e1"] == []


def test_minimum_score_filters_candidates():
    """
    The mentor should be excluded when their score is
    below the configured threshold.
    """

    mentor = create_mentor(
        mentor_id="m1",
        skills=[],
    )

    mentee = create_mentee()

    generator = CandidateGenerator(
        minimum_score=0.7,
    )

    result = generator.generate(
        [mentor],
        [mentee],
    )

    assert result["e1"] == []


def test_candidate_contains_features():
    mentor = create_mentor(
        mentor_id="m1",
        skills=[
            "Python",
            "Machine Learning",
        ],
    )

    mentee = create_mentee()

    generator = CandidateGenerator()

    result = generator.generate(
        [mentor],
        [mentee],
    )

    candidate = result["e1"][0]

    assert candidate.mentor_id == "m1"
    assert candidate.mentee_id == "e1"
    assert candidate.score > 0

    assert "skill_score" in candidate.features
    assert "expertise_score" in candidate.features
    assert "industry_score" in candidate.features
    assert "availability_score" in candidate.features
    assert "final_score" in candidate.features


def test_generate_flat_returns_all_candidates():
    mentors = [
        create_mentor(
            mentor_id="m1",
            skills=[
                "Python",
                "Machine Learning",
            ],
        ),
        create_mentor(
            mentor_id="m2",
            skills=["Python"],
        ),
    ]

    mentees = [
        create_mentee("e1"),
        create_mentee("e2"),
    ]

    generator = CandidateGenerator()

    candidates = generator.generate_flat(
        mentors,
        mentees,
    )

    assert len(candidates) == 4

    assert {
        candidate.mentor_id
        for candidate in candidates
    } == {
        "m1",
        "m2",
    }

    assert {
        candidate.mentee_id
        for candidate in candidates
    } == {
        "e1",
        "e2",
    }