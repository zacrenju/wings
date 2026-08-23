
from matching_engine.models.mentor import Mentor
from matching_engine.models.mentee import Mentee
from matching_engine.models.match import Match
from matching_engine.service.matching_service import MatchingService


def create_mentor(
    mentor_id: str,
    name: str = "John",
    skills: list[str] | None = None,
    expertise: list[str] | None = None,
    industry: str = "Aviation",
    years_experience: int = 10,
    experience_level: str = "senior",
    mentoring_topics: list[str] | None = None,
    availability: list[str] | None = None,
    max_mentees: int = 1,
    current_mentees: int = 0,
) -> Mentor:
    return Mentor(
        id=mentor_id,
        name=name,
        skills=skills or ["Python"],
        expertise=expertise or ["Machine Learning"],
        industry=industry,
        years_experience=years_experience,
        experience_level=experience_level,
        mentoring_topics=(
            mentoring_topics
            or ["Machine Learning"]
        ),
        availability=(
            availability
            or ["Monday", "Wednesday"]
        ),
        preferred_mentee_experience_levels=[
            "junior",
        ],
        preferred_industries=[
            industry,
        ],
        max_mentees=max_mentees,
        current_mentees=current_mentees,
    )


def create_mentee(
    mentee_id: str,
    name: str = "Alice",
    skills: list[str] | None = None,
    skills_to_learn: list[str] | None = None,
    industry: str = "Aviation",
    years_experience: int = 3,
    experience_level: str = "junior",
    goals: list[str] | None = None,
    interests: list[str] | None = None,
    availability: list[str] | None = None,
) -> Mentee:
    return Mentee(
        id=mentee_id,
        name=name,
        skills=skills or ["Python"],
        skills_to_learn=(
            skills_to_learn
            or ["Python", "Machine Learning"]
        ),
        industry=industry,
        years_experience=years_experience,
        experience_level=experience_level,
        goals=goals or ["Learn Machine Learning"],
        interests=(
            interests
            or ["Machine Learning"]
        ),
        availability=(
            availability
            or ["Monday", "Wednesday"]
        ),
        preferred_industries=[
            industry,
        ],
        preferred_mentor_experience_levels=[
            "senior",
        ],
        preferred_mentor_topics=[
            "Machine Learning",
        ],
    )


def test_single_mentor_single_mentee():
    """
    A single compatible mentor and mentee should
    produce exactly one Match.
    """

    mentor = create_mentor("m1")
    mentee = create_mentee("e1")

    service = MatchingService()

    result = service.match(
        [mentor],
        [mentee],
    )

    assert len(result) == 1

    match = result[0]

    assert isinstance(match, Match)
    assert match.mentor_id == "m1"
    assert match.mentee_id == "e1"

    assert 0.0 <= match.score <= 1.0
    assert match.is_valid is True


def test_best_mentor_is_selected():
    """
    When multiple mentors are available for one mentee,
    the highest-scoring mentor should be selected.

    mentor_1 has only Python in its skills with no
    expertise or mentoring_topics, so its capability set
    is strictly smaller than mentor_2's.
    mentor_2 covers both Python and Machine Learning, which
    is exactly what the mentee wants to learn.

    Note: create_mentor uses `or` for defaults so empty lists
    cannot be passed through it — mentor_1 is built directly.
    """

    mentor_1 = Mentor(
        id="m1",
        name="John",
        skills=["Python"],
        expertise=[],
        industry="Aviation",
        years_experience=10,
        experience_level="senior",
        mentoring_topics=[],
        availability=["Monday", "Wednesday"],
        preferred_mentee_experience_levels=["junior"],
        preferred_industries=["Aviation"],
    )

    mentor_2 = create_mentor(
        "m2",
        skills=[
            "Python",
            "Machine Learning",
        ],
    )

    mentee = create_mentee("e1")

    service = MatchingService()

    result = service.match(
        [mentor_1, mentor_2],
        [mentee],
    )

    assert len(result) == 1

    assert result[0].mentor_id == "m2"
    assert result[0].mentee_id == "e1"


def test_multiple_mentees_respect_mentor_capacity():
    """
    A mentor with capacity two should be able to
    receive two mentees.
    """

    mentor = create_mentor(
        "m1",
        max_mentees=2,
    )

    mentee_1 = create_mentee("e1")
    mentee_2 = create_mentee("e2")

    service = MatchingService()

    result = service.match(
        [mentor],
        [mentee_1, mentee_2],
    )

    assert len(result) == 2

    assert {
        match.mentee_id
        for match in result
    } == {
        "e1",
        "e2",
    }

    assert all(
        match.mentor_id == "m1"
        for match in result
    )


def test_mentor_capacity_one():
    """
    A mentor with capacity one cannot be assigned
    to more than one mentee.
    """

    mentor = create_mentor(
        "m1",
        max_mentees=1,
    )

    mentee_1 = create_mentee("e1")
    mentee_2 = create_mentee("e2")

    service = MatchingService()

    result = service.match(
        [mentor],
        [mentee_1, mentee_2],
    )

    assert len(result) == 1

    assert result[0].mentor_id == "m1"


def test_existing_mentees_reduce_capacity():
    """
    A mentor's current mentees should reduce the
    available capacity.
    """

    mentor = create_mentor(
        "m1",
        max_mentees=2,
        current_mentees=1,
    )

    mentee_1 = create_mentee("e1")
    mentee_2 = create_mentee("e2")

    service = MatchingService()

    result = service.match(
        [mentor],
        [mentee_1, mentee_2],
    )

    assert len(result) == 1


def test_multiple_mentors_multiple_mentees():
    """
    Multiple mentors and mentees should produce
    globally optimized assignments.
    """

    mentor_1 = create_mentor(
        "m1",
        skills=["Python"],
    )

    mentor_2 = create_mentor(
        "m2",
        skills=[
            "Python",
            "Machine Learning",
        ],
    )

    mentee_1 = create_mentee(
        "e1",
    )

    mentee_2 = create_mentee(
        "e2",
    )

    service = MatchingService()

    result = service.match(
        [mentor_1, mentor_2],
        [mentee_1, mentee_2],
    )

    assert len(result) == 2

    mentor_ids = {
        match.mentor_id
        for match in result
    }

    mentee_ids = {
        match.mentee_id
        for match in result
    }

    assert mentor_ids == {"m1", "m2"}
    assert mentee_ids == {"e1", "e2"}


def test_no_mentors_returns_empty():
    """
    No mentors means no matches.
    """

    mentee = create_mentee("e1")

    service = MatchingService()

    result = service.match(
        [],
        [mentee],
    )

    assert result == []


def test_no_mentees_returns_empty():
    """
    No mentees means no matches.
    """

    mentor = create_mentor("m1")

    service = MatchingService()

    result = service.match(
        [mentor],
        [],
    )

    assert result == []


def test_no_viable_candidates_returns_empty():
    """
    If the candidate generator produces no viable
    candidates, the service should return no matches.

    All scoring dimensions are deliberately mismatched so
    the final score is 0.0 and the candidate is filtered out:
      - skills/expertise/topics: Java vs Python       → 0.0
      - industry: Banking vs Aviation                 → 0.0
      - experience: junior mentor < senior mentee     → 0.5 (but
        experience weight is small; total remains 0.0 once
        industry and skill/expertise/topic are all 0)
      - availability: Saturday vs Sunday              → 0.0
    """

    mentor = Mentor(
        id="m1",
        name="John",
        skills=["Java"],
        expertise=["Java"],
        industry="Banking",
        years_experience=2,
        experience_level="junior",
        mentoring_topics=["Java"],
        availability=["Saturday"],
        preferred_mentee_experience_levels=["senior"],
        preferred_industries=["Banking"],
    )

    mentee = Mentee(
        id="e1",
        name="Alice",
        skills=["Python"],
        skills_to_learn=["Python"],
        interests=["Python"],
        industry="Aviation",
        years_experience=8,
        experience_level="senior",
        availability=["Sunday"],
        preferred_mentor_experience_levels=["senior"],
        preferred_industries=["Aviation"],
        preferred_mentor_topics=["Machine Learning"],
    )

    service = MatchingService()

    result = service.match(
        [mentor],
        [mentee],
    )

    assert result == []


def test_match_contains_score_components():
    """
    The Match object should contain the individual
    scoring components produced by the scorer.
    """

    mentor = create_mentor("m1")
    mentee = create_mentee("e1")

    service = MatchingService()

    result = service.match(
        [mentor],
        [mentee],
    )

    assert len(result) == 1

    match = result[0]

    assert 0.0 <= match.skill_score <= 1.0
    assert 0.0 <= match.experience_score <= 1.0
    assert 0.0 <= match.industry_score <= 1.0
    assert 0.0 <= match.availability_score <= 1.0


def test_match_contains_explanations():
    """
    A successful match should contain human-readable
    explanations.
    """

    mentor = create_mentor("m1")
    mentee = create_mentee("e1")

    service = MatchingService()

    result = service.match(
        [mentor],
        [mentee],
    )

    assert len(result) == 1

    match = result[0]

    assert isinstance(
        match.reasons,
        list,
    )

    assert len(match.reasons) > 0


def test_match_has_no_constraint_violations():
    """
    A successfully generated match should not contain
    constraint violations.
    """

    mentor = create_mentor("m1")
    mentee = create_mentee("e1")

    service = MatchingService()

    result = service.match(
        [mentor],
        [mentee],
    )

    assert len(result) == 1

    match = result[0]

    assert match.is_valid is True
    assert match.constraint_violations == []


def test_results_are_sorted_by_score():
    """
    Final matches should be returned from highest score
    to lowest score.
    """

    mentors = [
        create_mentor(
            "m1",
            skills=["Python"],
        ),
        create_mentor(
            "m2",
            skills=[
                "Python",
                "Machine Learning",
            ],
        ),
    ]

    mentees = [
        create_mentee("e1"),
        create_mentee("e2"),
    ]

    service = MatchingService()

    result = service.match(
        mentors,
        mentees,
    )

    scores = [
        match.score
        for match in result
    ]

    assert scores == sorted(
        scores,
        reverse=True,
    )


def test_match_ids_are_unique():
    """
    Each mentee should appear at most once in the
    final assignments.
    """

    mentors = [
        create_mentor(
            "m1",
            max_mentees=2,
        ),
        create_mentor(
            "m2",
            max_mentees=2,
        ),
    ]

    mentees = [
        create_mentee("e1"),
        create_mentee("e2"),
        create_mentee("e3"),
    ]

    service = MatchingService()

    result = service.match(
        mentors,
        mentees,
    )

    mentee_ids = [
        match.mentee_id
        for match in result
    ]

    assert len(mentee_ids) == len(
        set(mentee_ids)
    )
