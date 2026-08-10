from matching_engine.models.mentor import Mentor
from matching_engine.models.mentee import Mentee
from matching_engine.scoring.scorer import MatchScorer


def test_perfect_match():
    mentor = Mentor(
        id="m1",
        name="John",
        skills=["Python", "Machine Learning"],
        expertise=["Machine Learning"],
        industry="Aviation",
        years_experience=10,
        experience_level="senior",
        mentoring_topics=["Machine Learning"],
        availability=["Monday", "Wednesday"],
        preferred_industries=["Aviation"],
    )

    mentee = Mentee(
        id="e1",
        name="Alice",
        skills=["Python"],
        skills_to_learn=[
            "Python",
            "Machine Learning",
        ],
        industry="Aviation",
        years_experience=3,
        experience_level="junior",
        availability=["Monday", "Wednesday"],
        preferred_mentor_topics=["Machine Learning"],
    )

    scorer = MatchScorer()

    result = scorer.score(mentor, mentee)

    assert result["skill_score"] == 1.0
    assert result["expertise_score"] == 1.0
    assert result["industry_score"] == 1.0
    assert result["experience_score"] == 1.0
    assert result["availability_score"] == 1.0
    assert result["topic_score"] == 1.0

    assert result["final_score"] == 1.0


def test_partial_match():
    mentor = Mentor(
        id="m1",
        name="John",
        skills=["Python"],
        expertise=["Machine Learning"],
        industry="Aviation",
        years_experience=10,
        experience_level="senior",
        mentoring_topics=["Machine Learning"],
        availability=["Monday"],
    )

    mentee = Mentee(
        id="e1",
        name="Alice",
        skills_to_learn=[
            "Python",
            "Machine Learning",
            "Kubernetes",
        ],
        industry="Aviation",
        years_experience=3,
        experience_level="junior",
        availability=["Monday", "Tuesday"],
        preferred_mentor_topics=["Machine Learning"],
    )

    scorer = MatchScorer()

    result = scorer.score(mentor, mentee)

    # Python + Machine Learning = 2/3
    assert result["skill_score"] == round(
        2 / 3,
        4,
    )

    assert result["expertise_score"] == round(
        2 / 3,
        4,
   )

    assert result["industry_score"] == 1.0

    assert result["experience_score"] == 1.0

    # Monday overlaps, Tuesday does not.
    assert result["availability_score"] == 0.5

    assert result["topic_score"] == 1.0

    expected_score = (
    (2 / 3) * 0.40
    + (2 / 3) * 0.20
    + 1.0 * 0.15
    + 1.0 * 0.10
    + 0.5 * 0.10
    + 1.0 * 0.05
    )

    assert result["final_score"] == round(
        expected_score,
        4,
    )


def test_no_skill_match():
    mentor = Mentor(
        id="m1",
        name="John",
        skills=["Java"],
        expertise=["Spring"],
        industry="Banking",
        years_experience=10,
        experience_level="senior",
        mentoring_topics=["Java"],
    )

    mentee = Mentee(
        id="e1",
        name="Alice",
        skills_to_learn=[
            "Python",
            "Machine Learning",
        ],
        industry="Aviation",
        years_experience=2,
        experience_level="junior",
    )

    scorer = MatchScorer()

    result = scorer.score(mentor, mentee)

    assert result["skill_score"] == 0.0
    assert result["expertise_score"] == 0.0
    assert result["industry_score"] == 0.0
    assert result["experience_score"] == 1.0
    assert result["availability_score"] == 0.0
    assert result["topic_score"] == 0.0


def test_industry_match():
    mentor = Mentor(
        id="m1",
        name="John",
        industry="Aviation",
    )

    mentee = Mentee(
        id="e1",
        name="Alice",
        industry="Aviation",
    )

    scorer = MatchScorer()

    result = scorer.score(mentor, mentee)

    assert result["industry_score"] == 1.0


def test_industry_preference_match():
    mentor = Mentor(
        id="m1",
        name="John",
        industry="Technology",
        preferred_industries=["Aviation"],
    )

    mentee = Mentee(
        id="e1",
        name="Alice",
        industry="Aviation",
    )

    scorer = MatchScorer()

    result = scorer.score(mentor, mentee)

    assert result["industry_score"] == 1.0


def test_industry_mismatch():
    mentor = Mentor(
        id="m1",
        name="John",
        industry="Banking",
    )

    mentee = Mentee(
        id="e1",
        name="Alice",
        industry="Aviation",
    )

    scorer = MatchScorer()

    result = scorer.score(mentor, mentee)

    assert result["industry_score"] == 0.0


def test_experience_level_match():
    mentor = Mentor(
        id="m1",
        name="John",
        experience_level="senior",
        years_experience=10,
    )

    mentee = Mentee(
        id="e1",
        name="Alice",
        experience_level="junior",
        years_experience=2,
    )

    scorer = MatchScorer()

    result = scorer.score(mentor, mentee)

    assert result["experience_score"] == 1.0


def test_experience_partial_match():
    mentor = Mentor(
        id="m1",
        name="John",
        experience_level="junior",
        years_experience=2,
    )

    mentee = Mentee(
        id="e1",
        name="Alice",
        experience_level="senior",
        years_experience=8,
    )

    scorer = MatchScorer()

    result = scorer.score(mentor, mentee)

    assert result["experience_score"] == 0.5


def test_availability_match():
    mentor = Mentor(
        id="m1",
        name="John",
        availability=[
            "Monday",
            "Wednesday",
        ],
    )

    mentee = Mentee(
        id="e1",
        name="Alice",
        availability=[
            "Monday",
            "Friday",
        ],
    )

    scorer = MatchScorer()

    result = scorer.score(mentor, mentee)

    assert result["availability_score"] == 0.5


def test_topic_match():
    mentor = Mentor(
        id="m1",
        name="John",
        mentoring_topics=[
            "Machine Learning",
            "Python",
        ],
    )

    mentee = Mentee(
        id="e1",
        name="Alice",
        preferred_mentor_topics=[
            "Machine Learning",
        ],
    )

    scorer = MatchScorer()

    result = scorer.score(mentor, mentee)

    assert result["topic_score"] == 1.0


def test_topic_mismatch():
    mentor = Mentor(
        id="m1",
        name="John",
        mentoring_topics=[
            "Java",
        ],
    )

    mentee = Mentee(
        id="e1",
        name="Alice",
        preferred_mentor_topics=[
            "Machine Learning",
        ],
    )

    scorer = MatchScorer()

    result = scorer.score(mentor, mentee)

    assert result["topic_score"] == 0.0


def test_score_is_between_zero_and_one():
    mentor = Mentor(
        id="m1",
        name="John",
        skills=["Python"],
        expertise=["Machine Learning"],
        industry="Aviation",
        years_experience=10,
        experience_level="senior",
        mentoring_topics=["RAG"],
        availability=["Monday"],
    )

    mentee = Mentee(
        id="e1",
        name="Alice",
        skills_to_learn=[
            "Python",
            "Machine Learning",
        ],
        industry="Aviation",
        years_experience=3,
        experience_level="junior",
        availability=["Monday"],
        preferred_mentor_topics=["RAG"],
    )

    scorer = MatchScorer()

    result = scorer.score(mentor, mentee)

    assert 0.0 <= result["final_score"] <= 1.0