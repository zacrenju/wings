"""
Tests for MatchingService.recommend() — top-k mentor recommendations.
"""
from matching_engine.models.mentor import Mentor
from matching_engine.models.mentee import Mentee
from matching_engine.models.match import Match
from matching_engine.service.matching_service import MatchingService


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

def make_mentor(
    mentor_id: str,
    skills: list[str],
    expertise: list[str] | None = None,
    mentoring_topics: list[str] | None = None,
    industry: str = "technology",
    years_experience: int = 10,
    experience_level: str = "senior",
    availability: list[str] | None = None,
    max_mentees: int = 3,
) -> Mentor:
    return Mentor(
        id=mentor_id,
        name=f"Mentor {mentor_id}",
        skills=skills,
        expertise=expertise or [],
        industry=industry,
        years_experience=years_experience,
        experience_level=experience_level,
        mentoring_topics=mentoring_topics or [],
        availability=availability or ["Monday", "Wednesday"],
        preferred_mentee_experience_levels=["junior", "mid"],
        preferred_industries=[industry],
        max_mentees=max_mentees,
    )


def make_mentee(
    mentee_id: str,
    skills_to_learn: list[str],
    industry: str = "technology",
    experience_level: str = "junior",
    years_experience: int = 2,
    availability: list[str] | None = None,
) -> Mentee:
    return Mentee(
        id=mentee_id,
        name=f"Mentee {mentee_id}",
        skills=[],
        skills_to_learn=skills_to_learn,
        industry=industry,
        experience_level=experience_level,
        years_experience=years_experience,
        availability=availability or ["Monday", "Wednesday"],
        preferred_mentor_experience_levels=["senior"],
        preferred_industries=[industry],
        preferred_mentor_topics=skills_to_learn[:1],
    )


# ---------------------------------------------------------------------------
# Basic behaviour
# ---------------------------------------------------------------------------

def test_recommend_returns_dict_keyed_by_mentee_id():
    mentors = [
        make_mentor("m1", skills=["python"]),
        make_mentor("m2", skills=["python", "machine-learning"]),
    ]
    mentee = make_mentee("e1", skills_to_learn=["python", "machine-learning"])

    service = MatchingService()
    result = service.recommend(mentors, [mentee], top_k=3)

    assert isinstance(result, dict)
    assert "e1" in result


def test_recommend_results_are_match_objects():
    mentors = [make_mentor("m1", skills=["python"])]
    mentee = make_mentee("e1", skills_to_learn=["python"])

    service = MatchingService()
    result = service.recommend(mentors, [mentee], top_k=3)

    for match in result["e1"]:
        assert isinstance(match, Match)
        assert 0.0 <= match.score <= 1.0
        assert match.mentee_id == "e1"


def test_recommend_sorted_by_descending_score():
    mentors = [
        make_mentor("m1", skills=["java"]),
        make_mentor("m2", skills=["python", "machine-learning"],
                    mentoring_topics=["machine-learning"]),
        make_mentor("m3", skills=["python"]),
    ]
    mentee = make_mentee("e1", skills_to_learn=["python", "machine-learning"])

    service = MatchingService()
    result = service.recommend(mentors, [mentee], top_k=3)

    scores = [m.score for m in result["e1"]]
    assert scores == sorted(scores, reverse=True), (
        "Recommendations must be ordered highest score first"
    )


def test_recommend_top_k_limits_results():
    mentors = [
        make_mentor("m1", skills=["python"]),
        make_mentor("m2", skills=["python", "machine-learning"]),
        make_mentor("m3", skills=["python", "data-science"]),
        make_mentor("m4", skills=["python", "mlops"]),
    ]
    mentee = make_mentee("e1", skills_to_learn=["python"])

    service = MatchingService()

    assert len(service.recommend(mentors, [mentee], top_k=1)["e1"]) <= 1
    assert len(service.recommend(mentors, [mentee], top_k=2)["e1"]) <= 2
    assert len(service.recommend(mentors, [mentee], top_k=3)["e1"]) <= 3


def test_recommend_default_top_k_is_three():
    mentors = [
        make_mentor("m1", skills=["python"]),
        make_mentor("m2", skills=["python", "machine-learning"]),
        make_mentor("m3", skills=["python", "data-science"]),
        make_mentor("m4", skills=["python", "mlops"]),
    ]
    mentee = make_mentee("e1", skills_to_learn=["python"])

    service = MatchingService()
    result = service.recommend(mentors, [mentee])

    assert len(result["e1"]) <= 3


def test_recommend_best_mentor_ranks_first():
    """
    The mentor that most closely matches the mentee's desired skills
    should appear as the top recommendation.
    """
    mentor_perfect = make_mentor(
        "m_perfect",
        skills=["python", "machine-learning"],
        mentoring_topics=["machine-learning"],
    )
    mentor_partial = make_mentor(
        "m_partial",
        skills=["python"],
        expertise=[],
        mentoring_topics=[],
    )

    mentee = make_mentee("e1", skills_to_learn=["python", "machine-learning"])

    service = MatchingService()
    result = service.recommend([mentor_perfect, mentor_partial], [mentee], top_k=2)

    assert result["e1"][0].mentor_id == "m_perfect"


# ---------------------------------------------------------------------------
# Multiple mentees
# ---------------------------------------------------------------------------

def test_recommend_covers_all_mentees():
    mentors = [make_mentor("m1", skills=["python"])]
    mentees = [
        make_mentee("e1", skills_to_learn=["python"]),
        make_mentee("e2", skills_to_learn=["python"]),
    ]

    service = MatchingService()
    result = service.recommend(mentors, mentees, top_k=3)

    assert "e1" in result
    assert "e2" in result


def test_recommend_ignores_capacity_constraints():
    """
    recommend() must not cap results by mentor.max_mentees — the same
    mentor may appear in recommendations for multiple mentees.
    """
    mentor = make_mentor("m1", skills=["python"], max_mentees=1)
    mentees = [
        make_mentee("e1", skills_to_learn=["python"]),
        make_mentee("e2", skills_to_learn=["python"]),
    ]

    service = MatchingService()
    result = service.recommend([mentor], mentees, top_k=1)

    # Both mentees should still see m1 as a recommendation
    assert result.get("e1", [{}])[0].mentor_id == "m1"
    assert result.get("e2", [{}])[0].mentor_id == "m1"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_recommend_empty_mentors_returns_empty():
    mentee = make_mentee("e1", skills_to_learn=["python"])
    service = MatchingService()
    assert service.recommend([], [mentee], top_k=3) == {}


def test_recommend_empty_mentees_returns_empty():
    mentor = make_mentor("m1", skills=["python"])
    service = MatchingService()
    assert service.recommend([mentor], [], top_k=3) == {}


def test_recommend_top_k_zero_returns_empty():
    mentors = [make_mentor("m1", skills=["python"])]
    mentee = make_mentee("e1", skills_to_learn=["python"])
    service = MatchingService()
    assert service.recommend(mentors, [mentee], top_k=0) == {}


def test_recommend_no_eligible_candidates_omits_mentee():
    """
    A mentee for whom no mentor passes the eligibility check
    should be absent from the result dict.
    """
    mentor = Mentor(
        id="m1",
        name="Java Mentor",
        skills=["java"],
        expertise=["java"],
        industry="banking",
        years_experience=2,
        experience_level="junior",
        mentoring_topics=["java"],
        availability=["Saturday"],
        preferred_mentee_experience_levels=["senior"],
        preferred_industries=["banking"],
        max_mentees=5,
    )
    mentee = Mentee(
        id="e1",
        name="Python Mentee",
        skills=[],
        skills_to_learn=["python"],
        industry="technology",
        experience_level="senior",
        years_experience=8,
        availability=["Sunday"],
        preferred_mentor_experience_levels=["senior"],
        preferred_industries=["technology"],
        preferred_mentor_topics=["python"],
    )

    service = MatchingService()
    result = service.recommend([mentor], [mentee], top_k=3)

    assert "e1" not in result


def test_recommend_match_contains_score_components():
    mentor = make_mentor("m1", skills=["python", "machine-learning"],
                         mentoring_topics=["machine-learning"])
    mentee = make_mentee("e1", skills_to_learn=["python", "machine-learning"])

    service = MatchingService()
    result = service.recommend([mentor], [mentee], top_k=1)

    match = result["e1"][0]
    assert 0.0 <= match.skill_score <= 1.0
    assert 0.0 <= match.experience_score <= 1.0
    assert 0.0 <= match.industry_score <= 1.0
    assert 0.0 <= match.availability_score <= 1.0
    assert match.is_valid is True

