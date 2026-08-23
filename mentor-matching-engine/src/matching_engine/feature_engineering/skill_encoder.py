"""
Skill encoder — computes skill-based similarity between mentor and mentee.

Algorithm:
  Jaccard Similarity = |mentor_skills ∩ mentee_desired_skills|
                       / |mentor_skills ∪ mentee_desired_skills|

  Also accounts for partial skill name matches (e.g. "python" matches "python 3").
"""
from __future__ import annotations

from matching_engine.models.mentee import Mentee
from matching_engine.models.mentor import Mentor


def _normalise_skill(skill: str) -> str:
    return skill.strip().lower().replace("-", " ").replace("_", " ")


def _skill_set(skills: list[str]) -> set[str]:
    return {_normalise_skill(s) for s in skills}


def _mentor_skill_set(mentor: Mentor) -> set[str]:
    """Combine mentor skills, expertise, and mentoring topics into one set."""
    return _skill_set([*mentor.skills, *mentor.expertise, *mentor.mentoring_topics])


def _mentee_desired_set(mentee: Mentee) -> set[str]:
    """Use skills_to_learn, falling back to interests."""
    desired = _skill_set(mentee.skills_to_learn)
    if not desired:
        desired = _skill_set(mentee.interests)
    return desired


def jaccard_skill_score(mentor: Mentor, mentee: Mentee) -> float:
    """
    Compute Jaccard similarity between mentor expertise and mentee desired skills.

    Returns a float in [0.0, 1.0].
    """
    mentor_set = _mentor_skill_set(mentor)
    mentee_set = _mentee_desired_set(mentee)

    if not mentor_set or not mentee_set:
        return 0.0

    intersection = mentor_set & mentee_set
    union = mentor_set | mentee_set

    # Boost for partial matches (e.g. "python" in "python 3")
    partial_matches: set[str] = set()
    for ms in mentor_set:
        for mts in mentee_set:
            if ms not in intersection and mts not in intersection:
                if ms in mts or mts in ms:
                    partial_matches.add(ms)

    effective_intersection = len(intersection) + 0.5 * len(partial_matches)
    effective_union = len(union)

    return min(1.0, effective_intersection / effective_union)


def skill_coverage_score(mentor: Mentor, mentee: Mentee) -> float:
    """
    What fraction of the mentee's desired skills can the mentor cover?
    Coverage = |mentor_skills ∩ mentee_desired_skills| / |mentee_desired_skills|

    Complementary to Jaccard — focuses on mentee's perspective.
    Returns a float in [0.0, 1.0].
    """
    mentor_set = _mentor_skill_set(mentor)
    mentee_set = _mentee_desired_set(mentee)

    if not mentee_set:
        return 0.0

    covered = len(mentor_set & mentee_set)
    partial = sum(
        0.5 for ms in mentor_set
        for mts in mentee_set
        if ms not in (mentor_set & mentee_set) and (ms in mts or mts in ms)
    )

    return min(1.0, (covered + partial) / len(mentee_set))


def combined_skill_score(mentor: Mentor, mentee: Mentee) -> float:
    """
    Final skill score = 0.6 * coverage + 0.4 * jaccard.
    Coverage is weighted more because the mentee's perspective matters most.
    """
    coverage = skill_coverage_score(mentor, mentee)
    jaccard = jaccard_skill_score(mentor, mentee)
    return round(0.6 * coverage + 0.4 * jaccard, 6)

