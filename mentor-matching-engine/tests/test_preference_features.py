
from matching_engine.features.preference_features import (
    PreferenceFeatureExtractor,
)
from matching_engine.models.mentor import Mentor
from matching_engine.models.mentee import Mentee


def create_mentor(
    industry=None,
    experience_level=None,
    mentoring_topics=None,
):
    return Mentor(
        id="m1",
        name="John",
        industry=industry,
        experience_level=experience_level,
        mentoring_topics=mentoring_topics or [],
    )


def create_mentee(
    preferred_industries=None,
    preferred_mentor_experience_levels=None,
    preferred_mentor_topics=None,
):
    return Mentee(
        id="e1",
        name="Alice",
        preferred_industries=preferred_industries or [],
        preferred_mentor_experience_levels=(
            preferred_mentor_experience_levels or []
        ),
        preferred_mentor_topics=(
            preferred_mentor_topics or []
        ),
    )


def test_perfect_preference_match():
    """
    All mentee preferences are satisfied by the mentor.
    """

    mentor = create_mentor(
        industry="Aviation",
        experience_level="Senior",
        mentoring_topics=[
            "Machine Learning",
            "Leadership",
        ],
    )

    mentee = create_mentee(
        preferred_industries=["Aviation"],
        preferred_mentor_experience_levels=["Senior"],
        preferred_mentor_topics=[
            "Machine Learning",
            "Leadership",
        ],
    )

    extractor = PreferenceFeatureExtractor()

    result = extractor.extract(
        mentor,
        mentee,
    )

    assert result["industry_preference_score"] == 1.0
    assert result["experience_preference_score"] == 1.0
    assert result["topic_preference_score"] == 1.0
    assert result["preference_score"] == 1.0


def test_partial_topic_preference_match():
    """
    Only some preferred mentoring topics are provided
    by the mentor.
    """

    mentor = create_mentor(
        industry="Aviation",
        experience_level="Senior",
        mentoring_topics=[
            "Machine Learning",
            "Cloud",
        ],
    )

    mentee = create_mentee(
        preferred_mentor_topics=[
            "Machine Learning",
            "Cloud",
            "Leadership",
        ],
    )

    extractor = PreferenceFeatureExtractor()

    result = extractor.extract(
        mentor,
        mentee,
    )

    assert result["topic_preference_score"] == round(
        2 / 3,
        4,
    )

    # Only topic preference is applicable.
    assert result["preference_score"] == round(
        2 / 3,
        4,
    )


def test_no_preference_match():
    """
    None of the mentee preferences match the mentor.
    """

    mentor = create_mentor(
        industry="Finance",
        experience_level="Junior",
        mentoring_topics=[
            "Java",
            "Spring Boot",
        ],
    )

    mentee = create_mentee(
        preferred_industries=["Aviation"],
        preferred_mentor_experience_levels=["Senior"],
        preferred_mentor_topics=[
            "Python",
            "Machine Learning",
        ],
    )

    extractor = PreferenceFeatureExtractor()

    result = extractor.extract(
        mentor,
        mentee,
    )

    assert result["industry_preference_score"] == 0.0
    assert result["experience_preference_score"] == 0.0
    assert result["topic_preference_score"] == 0.0
    assert result["preference_score"] == 0.0


def test_preference_normalization():
    """
    Preference comparison should be case-insensitive
    and ignore surrounding whitespace.
    """

    mentor = create_mentor(
        industry=" Aviation ",
        experience_level=" SENIOR ",
        mentoring_topics=[
            " MACHINE LEARNING ",
        ],
    )

    mentee = create_mentee(
        preferred_industries=["aviation"],
        preferred_mentor_experience_levels=["senior"],
        preferred_mentor_topics=[
            "machine learning",
        ],
    )

    extractor = PreferenceFeatureExtractor()

    result = extractor.extract(
        mentor,
        mentee,
    )

    assert result["industry_preference_score"] == 1.0
    assert result["experience_preference_score"] == 1.0
    assert result["topic_preference_score"] == 1.0
    assert result["preference_score"] == 1.0


def test_multiple_preferred_industries():
    """
    The mentor should match if their industry is one
    of several preferred industries.
    """

    mentor = create_mentor(
        industry="Aviation",
    )

    mentee = create_mentee(
        preferred_industries=[
            "Technology",
            "Aviation",
            "Finance",
        ],
    )

    extractor = PreferenceFeatureExtractor()

    result = extractor.extract(
        mentor,
        mentee,
    )

    assert result["industry_preference_score"] == 1.0
    assert result["preference_score"] == 1.0


def test_multiple_preferred_experience_levels():
    """
    The mentor should match if their experience level
    is one of several preferred levels.
    """

    mentor = create_mentor(
        experience_level="Senior",
    )

    mentee = create_mentee(
        preferred_mentor_experience_levels=[
            "Mid",
            "Senior",
            "Principal",
        ],
    )

    extractor = PreferenceFeatureExtractor()

    result = extractor.extract(
        mentor,
        mentee,
    )

    assert result["experience_preference_score"] == 1.0
    assert result["preference_score"] == 1.0


def test_only_industry_preference_is_used():
    """
    When only industry preference is provided, the
    overall preference score should be based only
    on industry.
    """

    mentor = create_mentor(
        industry="Aviation",
        experience_level="Junior",
        mentoring_topics=["Java"],
    )

    mentee = create_mentee(
        preferred_industries=["Aviation"],
    )

    extractor = PreferenceFeatureExtractor()

    result = extractor.extract(
        mentor,
        mentee,
    )

    assert result["industry_preference_score"] == 1.0
    assert result["experience_preference_score"] == 0.0
    assert result["topic_preference_score"] == 0.0
    assert result["preference_score"] == 1.0


def test_only_experience_preference_is_used():
    """
    When only experience-level preference is provided,
    the overall score should be based only on experience.
    """

    mentor = create_mentor(
        industry="Finance",
        experience_level="Senior",
    )

    mentee = create_mentee(
        preferred_mentor_experience_levels=[
            "Senior",
        ],
    )

    extractor = PreferenceFeatureExtractor()

    result = extractor.extract(
        mentor,
        mentee,
    )

    assert result["industry_preference_score"] == 0.0
    assert result["experience_preference_score"] == 1.0
    assert result["topic_preference_score"] == 0.0
    assert result["preference_score"] == 1.0


def test_only_topic_preference_is_used():
    """
    When only topic preference is provided, the overall
    score should be based only on topics.
    """

    mentor = create_mentor(
        mentoring_topics=[
            "Machine Learning",
        ],
    )

    mentee = create_mentee(
        preferred_mentor_topics=[
            "Machine Learning",
        ],
    )

    extractor = PreferenceFeatureExtractor()

    result = extractor.extract(
        mentor,
        mentee,
    )

    assert result["industry_preference_score"] == 0.0
    assert result["experience_preference_score"] == 0.0
    assert result["topic_preference_score"] == 1.0
    assert result["preference_score"] == 1.0


def test_no_preferences():
    """
    If the mentee has no explicit preferences,
    preference score should be zero.
    """

    mentor = create_mentor(
        industry="Aviation",
        experience_level="Senior",
        mentoring_topics=["Python"],
    )

    mentee = create_mentee()

    extractor = PreferenceFeatureExtractor()

    result = extractor.extract(
        mentor,
        mentee,
    )

    assert result["industry_preference_score"] == 0.0
    assert result["experience_preference_score"] == 0.0
    assert result["topic_preference_score"] == 0.0
    assert result["preference_score"] == 0.0


def test_missing_mentor_industry():
    """
    A missing mentor industry cannot satisfy an industry
    preference.
    """

    mentor = create_mentor(
        industry=None,
    )

    mentee = create_mentee(
        preferred_industries=["Aviation"],
    )

    extractor = PreferenceFeatureExtractor()

    result = extractor.extract(
        mentor,
        mentee,
    )

    assert result["industry_preference_score"] == 0.0
    assert result["preference_score"] == 0.0


def test_missing_mentor_experience_level():
    """
    A missing mentor experience level cannot satisfy
    an experience-level preference.
    """

    mentor = create_mentor(
        experience_level=None,
    )

    mentee = create_mentee(
        preferred_mentor_experience_levels=[
            "Senior",
        ],
    )

    extractor = PreferenceFeatureExtractor()

    result = extractor.extract(
        mentor,
        mentee,
    )

    assert result["experience_preference_score"] == 0.0
    assert result["preference_score"] == 0.0


def test_missing_mentor_topics():
    """
    A mentor without mentoring topics cannot satisfy
    topic preferences.
    """

    mentor = create_mentor(
        mentoring_topics=[],
    )

    mentee = create_mentee(
        preferred_mentor_topics=[
            "Machine Learning",
        ],
    )

    extractor = PreferenceFeatureExtractor()

    result = extractor.extract(
        mentor,
        mentee,
    )

    assert result["topic_preference_score"] == 0.0
    assert result["preference_score"] == 0.0


def test_overall_preference_score_averages_applicable_preferences():
    """
    When all three preference categories are specified,
    the overall score should be the average of the
    applicable category scores.
    """

    mentor = create_mentor(
        industry="Aviation",
        experience_level="Senior",
        mentoring_topics=[
            "Machine Learning",
            "Cloud",
        ],
    )

    mentee = create_mentee(
        preferred_industries=["Aviation"],
        preferred_mentor_experience_levels=["Senior"],
        preferred_mentor_topics=[
            "Machine Learning",
            "Cloud",
            "Leadership",
        ],
    )

    extractor = PreferenceFeatureExtractor()

    result = extractor.extract(
        mentor,
        mentee,
    )

    expected = (
        1.0
        + 1.0
        + round(2 / 3, 4)
    ) / 3

    assert result["industry_preference_score"] == 1.0
    assert result["experience_preference_score"] == 1.0
    assert result["topic_preference_score"] == round(
        2 / 3,
        4,
    )

    assert result["preference_score"] == round(
        expected,
        4,
    )


def test_duplicate_topics_are_counted_once():
    """
    Duplicate preferred topics should not artificially
    increase the topic preference score.
    """

    mentor = create_mentor(
        mentoring_topics=[
            "Python",
        ],
    )

    mentee = create_mentee(
        preferred_mentor_topics=[
            "Python",
            "python",
            " Python ",
        ],
    )

    extractor = PreferenceFeatureExtractor()

    result = extractor.extract(
        mentor,
        mentee,
    )

    assert result["topic_preference_score"] == 1.0
    assert result["preference_score"] == 1.0