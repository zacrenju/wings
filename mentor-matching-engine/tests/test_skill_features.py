
from matching_engine.features.skill_features import (
    SkillFeatureExtractor,
)
from matching_engine.models.mentor import Mentor
from matching_engine.models.mentee import Mentee


def test_full_skill_match():
    mentor = Mentor(
        id="m1",
        name="John",
        skills=["Python", "AWS"],
        expertise=["Machine Learning"],
        mentoring_topics=["RAG"],
    )

    mentee = Mentee(
        id="e1",
        name="Alice",
        skills=["Python"],
        skills_to_learn=[
            "Python",
            "Machine Learning",
            "RAG",
        ],
    )

    extractor = SkillFeatureExtractor()

    features = extractor.extract(
        mentor,
        mentee,
    )

    assert features["skill_coverage"] == 1.0
    assert features["skill_overlap"] == 1.0
    assert features["missing_skills"] == 0.0


def test_partial_skill_match():
    mentor = Mentor(
        id="m1",
        name="John",
        skills=["Python"],
        expertise=["Machine Learning"],
    )

    mentee = Mentee(
        id="e1",
        name="Alice",
        skills_to_learn=[
            "Python",
            "Machine Learning",
            "Kubernetes",
            "Docker",
        ],
    )

    extractor = SkillFeatureExtractor()

    features = extractor.extract(
        mentor,
        mentee,
    )

    # Mentor can support 2 out of 4 requested skills.
    assert features["skill_coverage"] == 0.5
    assert features["skill_overlap"] == 0.5
    assert features["missing_skills"] == 2.0


def test_no_skill_match():
    mentor = Mentor(
        id="m1",
        name="John",
        skills=["Java", "Spring"],
    )

    mentee = Mentee(
        id="e1",
        name="Alice",
        skills_to_learn=[
            "Python",
            "Machine Learning",
        ],
    )

    extractor = SkillFeatureExtractor()

    features = extractor.extract(
        mentor,
        mentee,
    )

    assert features["skill_coverage"] == 0.0
    assert features["skill_overlap"] == 0.0
    assert features["missing_skills"] == 2.0


def test_empty_skills_to_learn():
    mentor = Mentor(
        id="m1",
        name="John",
        skills=["Python"],
    )

    mentee = Mentee(
        id="e1",
        name="Alice",
        skills_to_learn=[],
        interests=[],
    )

    extractor = SkillFeatureExtractor()

    features = extractor.extract(
        mentor,
        mentee,
    )

    assert features["skill_coverage"] == 0.0
    assert features["skill_overlap"] == 0.0
    assert features["missing_skills"] == 0.0
    assert features["mentee_skill_count"] == 0.0


def test_skill_normalization():
    mentor = Mentor(
        id="m1",
        name="John",
        skills=[
            "Python",
            " Machine Learning ",
        ],
    )

    mentee = Mentee(
        id="e1",
        name="Alice",
        skills_to_learn=[
            "python",
            "machine learning",
        ],
    )

    extractor = SkillFeatureExtractor()

    features = extractor.extract(
        mentor,
        mentee,
    )

    assert features["skill_coverage"] == 1.0


def test_mentor_expertise_counts_as_capability():
    mentor = Mentor(
        id="m1",
        name="John",
        expertise=[
            "Machine Learning",
        ],
    )

    mentee = Mentee(
        id="e1",
        name="Alice",
        skills_to_learn=[
            "Machine Learning",
        ],
    )

    extractor = SkillFeatureExtractor()

    features = extractor.extract(
        mentor,
        mentee,
    )

    assert features["skill_coverage"] == 1.0


def test_mentoring_topics_count_as_capability():
    mentor = Mentor(
        id="m1",
        name="John",
        mentoring_topics=[
            "LangGraph",
            "RAG",
        ],
    )

    mentee = Mentee(
        id="e1",
        name="Alice",
        skills_to_learn=[
            "RAG",
        ],
    )

    extractor = SkillFeatureExtractor()

    features = extractor.extract(
        mentor,
        mentee,
    )

    assert features["skill_coverage"] == 1.0


def test_interests_are_used_when_skills_to_learn_is_empty():
    mentor = Mentor(
        id="m1",
        name="John",
        skills=["Python"],
    )

    mentee = Mentee(
        id="e1",
        name="Alice",
        skills_to_learn=[],
        interests=["Python"],
    )

    extractor = SkillFeatureExtractor()

    features = extractor.extract(
        mentor,
        mentee,
    )

    assert features["skill_coverage"] == 1.0
    assert features["skill_overlap"] == 1.0
    assert features["missing_skills"] == 0.0