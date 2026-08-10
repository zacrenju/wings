
from __future__ import annotations

from typing import Iterable

from matching_engine.models.mentor import Mentor
from matching_engine.models.mentee import Mentee


class GoalFeatureExtractor:
    """
    Extract goal-based compatibility features between
    a mentor and mentee.

    Goal compatibility is based on whether the mentor's
    capabilities can support what the mentee wants to learn
    and achieve.

    Mentor capabilities:
        - skills
        - expertise
        - mentoring_topics

    Mentee objectives:
        - skills_to_learn
        - goals
        - interests
    """

    def extract(
        self,
        mentor: Mentor,
        mentee: Mentee,
    ) -> dict[str, float]:
        """
        Calculate goal compatibility features.

        Returns:
            Dictionary containing:

            - goal_score
            - goal_overlap
            - goal_coverage
            - matched_goals
            - missing_goals
            - capability_count
            - mentee_goal_count
        """

        mentor_capabilities = self._normalize(
            [
                *mentor.skills,
                *mentor.expertise,
                *mentor.mentoring_topics,
            ]
        )

        mentee_objectives = self._normalize(
            [
                *mentee.skills_to_learn,
                *mentee.goals,
                *mentee.interests,
            ]
        )

        if not mentee_objectives:
            return {
                "goal_score": 0.0,
                "goal_overlap": 0.0,
                "goal_coverage": 0.0,
                "matched_goals": 0.0,
                "missing_goals": 0.0,
                "capability_count": float(
                    len(mentor_capabilities)
                ),
                "mentee_goal_count": 0.0,
            }

        matched = (
            mentee_objectives
            & mentor_capabilities
        )

        missing = (
            mentee_objectives
            - mentor_capabilities
        )

        goal_score = (
            len(matched)
            / len(mentee_objectives)
        )

        return {
            "goal_score": round(
                goal_score,
                4,
            ),
            "goal_overlap": round(
                goal_score,
                4,
            ),
            "goal_coverage": round(
                goal_score,
                4,
            ),
            "matched_goals": float(
                len(matched)
            ),
            "missing_goals": float(
                len(missing)
            ),
            "capability_count": float(
                len(mentor_capabilities)
            ),
            "mentee_goal_count": float(
                len(mentee_objectives)
            ),
        }

    @staticmethod
    def _normalize(
        values: Iterable[str],
    ) -> set[str]:
        """
        Normalize values for comparison.

        Example:
            ["Python", " Machine Learning "]

        becomes:

            {"python", "machine learning"}
        """

        return {
            value.strip().lower()
            for value in values
            if value and value.strip()
        }