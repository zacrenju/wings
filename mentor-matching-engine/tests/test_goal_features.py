
from matching_engine.features.goal_features import GoalFeatureExtractor
from matching_engine.models.mentor import Mentor
from matching_engine.models.mentee import Mentee


def create_mentor(
    skills=None,
    expertise=None,
    mentoring_topics=None,
):
    return Mentor(
        id="m1",
        name="John",
        skills=skills or [],
        expertise=expertise or [],
        mentoring_topics=mentoring_topics or [],
    )


def create_mentee(
    skills_to_learn=None,
    goals=None,
    interests=None,
):
    return Mentee(
        id="e1",
        name="Alice",
        skills_to_learn=skills_to_learn or [],
        goals=goals or [],
        interests=interests or [],
    )


def test_perfect_goal_match():
    """
    All mentee objectives are supported by the mentor.
    """

    mentor = create_mentor(
        skills=[
            "Python",
            "Machine Learning",
        ],
        expertise=[
            "Deep Learning",
        ],
        mentoring_topics=[
            "AI",
        ],
    )

    mentee = create_mentee(
        skills_to_learn=[
            "Python",
            "Machine Learning",
        ],
        goals=[
            "Deep Learning",
        ],
        interests=[
            "AI",
        ],
    )

    extractor = GoalFeatureExtractor()

    result = extractor.extract(
        mentor,
        mentee,
    )

    assert result["goal_score"] == 1.0
    assert result["goal_overlap"] == 1.0
    assert result["goal_coverage"] == 1.0

    assert result["matched_goals"] == 4.0
    assert result["missing_goals"] == 0.0


def test_partial_goal_match():
    """
    Only some of the mentee objectives are supported
    by the mentor.
    """

    mentor = create_mentor(
        skills=["Python"],
        expertise=["Machine Learning"],
        mentoring_topics=[],
    )

    mentee = create_mentee(
        skills_to_learn=[
            "Python",
            "Machine Learning",
            "Kubernetes",
        ],
    )

    extractor = GoalFeatureExtractor()

    result = extractor.extract(
        mentor,
        mentee,
    )

    assert result["goal_score"] == round(
        2 / 3,
        4,
    )

    assert result["goal_overlap"] == round(
        2 / 3,
        4,
    )

    assert result["goal_coverage"] == round(
        2 / 3,
        4,
    )

    assert result["matched_goals"] == 2.0
    assert result["missing_goals"] == 1.0


def test_no_goal_match():
    """
    None of the mentee objectives are supported
    by the mentor.
    """

    mentor = create_mentor(
        skills=["Java"],
        expertise=["Spring Boot"],
        mentoring_topics=["Microservices"],
    )

    mentee = create_mentee(
        skills_to_learn=[
            "Python",
            "Machine Learning",
        ],
    )

    extractor = GoalFeatureExtractor()

    result = extractor.extract(
        mentor,
        mentee,
    )

    assert result["goal_score"] == 0.0
    assert result["goal_overlap"] == 0.0
    assert result["goal_coverage"] == 0.0

    assert result["matched_goals"] == 0.0
    assert result["missing_goals"] == 2.0


def test_goal_normalization():
    """
    Goal matching should be case-insensitive and
    ignore surrounding whitespace.
    """

    mentor = create_mentor(
        skills=[
            " Python ",
            "MACHINE LEARNING",
        ],
    )

    mentee = create_mentee(
        skills_to_learn=[
            "python",
            " machine learning ",
        ],
    )

    extractor = GoalFeatureExtractor()

    result = extractor.extract(
        mentor,
        mentee,
    )

    assert result["goal_score"] == 1.0
    assert result["matched_goals"] == 2.0
    assert result["missing_goals"] == 0.0


def test_expertise_counts_as_capability():
    """
    Mentor expertise should contribute to goal
    compatibility.
    """

    mentor = create_mentor(
        expertise=["Machine Learning"],
    )

    mentee = create_mentee(
        skills_to_learn=["Machine Learning"],
    )

    extractor = GoalFeatureExtractor()

    result = extractor.extract(
        mentor,
        mentee,
    )

    assert result["goal_score"] == 1.0
    assert result["matched_goals"] == 1.0


def test_mentoring_topics_count_as_capability():
    """
    Mentor mentoring topics should contribute to
    goal compatibility.
    """

    mentor = create_mentor(
        mentoring_topics=["Leadership"],
    )

    mentee = create_mentee(
        goals=["Leadership"],
    )

    extractor = GoalFeatureExtractor()

    result = extractor.extract(
        mentor,
        mentee,
    )

    assert result["goal_score"] == 1.0
    assert result["matched_goals"] == 1.0


def test_goals_and_interests_are_used():
    """
    Goals and interests should both contribute to
    the objective set.
    """

    mentor = create_mentor(
        expertise=[
            "Leadership",
            "Aviation",
        ],
    )

    mentee = create_mentee(
        goals=["Leadership"],
        interests=["Aviation"],
    )

    extractor = GoalFeatureExtractor()

    result = extractor.extract(
        mentor,
        mentee,
    )

    assert result["goal_score"] == 1.0
    assert result["matched_goals"] == 2.0


def test_empty_mentee_objectives():
    """
    If the mentee has no objectives, goal compatibility
    should be zero rather than producing a division error.
    """

    mentor = create_mentor(
        skills=["Python"],
        expertise=["Machine Learning"],
    )

    mentee = create_mentee()

    extractor = GoalFeatureExtractor()

    result = extractor.extract(
        mentor,
        mentee,
    )

    assert result["goal_score"] == 0.0
    assert result["goal_overlap"] == 0.0
    assert result["goal_coverage"] == 0.0

    assert result["matched_goals"] == 0.0
    assert result["missing_goals"] == 0.0


def test_empty_mentor_capabilities():
    """
    A mentor without skills, expertise, or mentoring
    topics cannot satisfy mentee objectives.
    """

    mentor = create_mentor()

    mentee = create_mentee(
        skills_to_learn=[
            "Python",
            "Machine Learning",
        ],
    )

    extractor = GoalFeatureExtractor()

    result = extractor.extract(
        mentor,
        mentee,
    )

    assert result["goal_score"] == 0.0
    assert result["matched_goals"] == 0.0
    assert result["missing_goals"] == 2.0


def test_duplicate_objectives_are_counted_once():
    """
    Duplicate objectives should not artificially increase
    the goal score because objectives are normalized into
    a set.
    """

    mentor = create_mentor(
        skills=["Python"],
    )

    mentee = create_mentee(
        skills_to_learn=[
            "Python",
            "python",
            " Python ",
        ],
    )

    extractor = GoalFeatureExtractor()

    result = extractor.extract(
        mentor,
        mentee,
    )

    assert result["goal_score"] == 1.0
    assert result["matched_goals"] == 1.0
    assert result["missing_goals"] == 0.0


def test_feature_counts_are_correct():
    """
    The extractor should expose the number of unique
    mentor capabilities and mentee objectives.
    """

    mentor = create_mentor(
        skills=[
            "Python",
            "Machine Learning",
        ],
        expertise=[
            "Machine Learning",
            "Deep Learning",
        ],
        mentoring_topics=[
            "AI",
        ],
    )

    mentee = create_mentee(
        skills_to_learn=[
            "Python",
            "Kubernetes",
        ],
        goals=[
            "Deep Learning",
        ],
        interests=[
            "AI",
        ],
    )

    extractor = GoalFeatureExtractor()

    result = extractor.extract(
        mentor,
        mentee,
    )

    # Unique mentor capabilities:
    # Python, Machine Learning, Deep Learning, AI
    assert result["capability_count"] == 4.0

    # Unique mentee objectives:
    # Python, Kubernetes, Deep Learning, AI
    assert result["mentee_goal_count"] == 4.0

    # Python, Deep Learning and AI match.
    assert result["matched_goals"] == 3.0
    assert result["missing_goals"] == 1.0

    assert result["goal_score"] == 0.75