
from __future__ import annotations

from matching_engine.features.goal_features import GoalFeatureExtractor
from matching_engine.features.preference_features import (
    PreferenceFeatureExtractor,
)
from matching_engine.features.skill_features import SkillFeatureExtractor
from matching_engine.models.mentor import Mentor
from matching_engine.models.mentee import Mentee


class MatchScorer:
    """
    Calculate mentor-mentee compatibility scores.

    Current final-score weights:

        Skill          40%
        Expertise      20%
        Industry       15%
        Experience     10%
        Availability   10%
        Topic           5%

    Total = 100%.

    Goal and broader preference features are extracted
    and returned for explainability/future scoring,
    but are not currently part of the weighted score.
    """

    WEIGHTS = {
        "skill_score": 0.40,
        "expertise_score": 0.20,
        "industry_score": 0.15,
        "experience_score": 0.10,
        "availability_score": 0.10,
        "topic_score": 0.05,
    }

    def __init__(self) -> None:
        self.skill_extractor = SkillFeatureExtractor()
        self.goal_extractor = GoalFeatureExtractor()
        self.preference_extractor = PreferenceFeatureExtractor()

    def score(
        self,
        mentor: Mentor,
        mentee: Mentee,
    ) -> dict[str, float]:
        """
        Calculate compatibility between one mentor
        and one mentee.
        """

        # -------------------------------------------------
        # Feature extraction
        # -------------------------------------------------

        skill_features = self.skill_extractor.extract(
            mentor,
            mentee,
        )

        goal_features = self.goal_extractor.extract(
            mentor,
            mentee,
        )

        preference_features = (
            self.preference_extractor.extract(
                mentor,
                mentee,
            )
        )

        # -------------------------------------------------
        # Primary scores
        # -------------------------------------------------

        skill_score = self._get_skill_score(
            skill_features
        )

        goal_score = goal_features["goal_score"]

        expertise_score = self._expertise_score(
            mentor,
            mentee,
        )

        industry_score = self._industry_score(
            mentor,
            mentee,
        )

        experience_score = self._experience_score(
            mentor,
            mentee,
        )

        availability_score = self._availability_score(
            mentor,
            mentee,
        )

        # -------------------------------------------------
        # Preference / topic scores
        # -------------------------------------------------

        preference_score = (
            preference_features["preference_score"]
        )

        topic_score = (
            preference_features[
                "topic_preference_score"
            ]
        )

        industry_preference_score = (
            preference_features[
                "industry_preference_score"
            ]
        )

        experience_preference_score = (
            preference_features[
                "experience_preference_score"
            ]
        )

        # -------------------------------------------------
        # Final weighted score
        # -------------------------------------------------

        final_score = (
            skill_score
            * self.WEIGHTS["skill_score"]
            + expertise_score
            * self.WEIGHTS["expertise_score"]
            + industry_score
            * self.WEIGHTS["industry_score"]
            + experience_score
            * self.WEIGHTS["experience_score"]
            + availability_score
            * self.WEIGHTS["availability_score"]
            + topic_score
            * self.WEIGHTS["topic_score"]
        )

        # -------------------------------------------------
        # Return all explainable scores
        # -------------------------------------------------

        return {
            "skill_score": round(
                skill_score,
                4,
            ),
            "goal_score": round(
                goal_score,
                4,
            ),
            "expertise_score": round(
                expertise_score,
                4,
            ),
            "industry_score": round(
                industry_score,
                4,
            ),
            "experience_score": round(
                experience_score,
                4,
            ),
            "availability_score": round(
                availability_score,
                4,
            ),
            "preference_score": round(
                preference_score,
                4,
            ),
            "topic_score": round(
                topic_score,
                4,
            ),
            "industry_preference_score": round(
                industry_preference_score,
                4,
            ),
            "experience_preference_score": round(
                experience_preference_score,
                4,
            ),
            "final_score": round(
                final_score,
                4,
            ),
        }

    # =====================================================
    # Skill
    # =====================================================

    @staticmethod
    def _get_skill_score(
        skill_features: dict[str, float],
    ) -> float:
        """
        Get the normalized skill compatibility score.

        SkillFeatureExtractor currently exposes
        skill_coverage rather than skill_score.
        """

        if "skill_score" in skill_features:
            return skill_features["skill_score"]

        return skill_features.get(
            "skill_coverage",
            0.0,
        )

    # =====================================================
    # Utility
    # =====================================================

    @staticmethod
    def _normalize(
        values: list[str],
    ) -> set[str]:
        """Normalize string values for comparison."""

        return {
            value.strip().lower()
            for value in values
            if value and value.strip()
        }

    # =====================================================
    # Expertise
    # =====================================================

    def _expertise_score(
        self,
        mentor: Mentor,
        mentee: Mentee,
    ) -> float:
        """
        Measure how well the mentor's expertise covers
        the mentee's desired learning areas.

        Mentor capabilities include:

            - skills
            - expertise
            - mentoring_topics
        """

        mentor_capabilities = self._normalize(
            [
                *mentor.skills,
                *mentor.expertise,
                *mentor.mentoring_topics,
            ]
        )

        mentee_targets = self._normalize(
            mentee.skills_to_learn
        )

        # Fall back to interests when the mentee
        # has not specified learning skills.
        if not mentee_targets:
            mentee_targets = self._normalize(
                mentee.interests
            )

        if not mentee_targets:
            return 0.0

        overlap = (
            mentor_capabilities
            & mentee_targets
        )

        return len(overlap) / len(mentee_targets)

    # =====================================================
    # Industry
    # =====================================================

    def _industry_score(
        self,
        mentor: Mentor,
        mentee: Mentee,
    ) -> float:
        """
        Measure industry compatibility.

        A direct industry match receives 1.0.

        A match between the mentee's industry and
        the mentor's preferred industries also receives
        1.0.

        Otherwise the score is 0.0.
        """

        if not mentee.industry:
            return 0.0

        mentee_industry = (
            mentee.industry.strip().lower()
        )

        # Direct industry match.
        if mentor.industry:
            mentor_industry = (
                mentor.industry.strip().lower()
            )

            if mentor_industry == mentee_industry:
                return 1.0

        # Mentor prefers the mentee's industry.
        preferred_industries = self._normalize(
            mentor.preferred_industries
        )

        if mentee_industry in preferred_industries:
            return 1.0

        return 0.0

    # =====================================================
    # Experience
    # =====================================================

    def _experience_score(
        self,
        mentor: Mentor,
        mentee: Mentee,
    ) -> float:
        """
        Measure mentor experience compatibility.

        Rules:

            Mentor >= mentee level -> 1.0
            Mentor < mentee level  -> 0.5
            Missing/unknown level  -> 0.0

        This reflects the current test/scoring contract.
        """

        if (
            not mentor.experience_level
            or not mentee.experience_level
        ):
            return 0.0

        levels = {
            "intern": 0,
            "student": 0,
            "junior": 1,
            "mid": 2,
            "mid-level": 2,
            "senior": 3,
            "lead": 4,
            "staff": 5,
            "principal": 5,
            "executive": 6,
        }

        mentor_level = levels.get(
            mentor.experience_level.strip().lower()
        )

        mentee_level = levels.get(
            mentee.experience_level.strip().lower()
        )

        if (
            mentor_level is None
            or mentee_level is None
        ):
            return 0.0

        if mentor_level >= mentee_level:
            return 1.0

        return 0.5

    # =====================================================
    # Availability
    # =====================================================

    def _availability_score(
        self,
        mentor: Mentor,
        mentee: Mentee,
    ) -> float:
        """
        Measure availability overlap.

        Score is the proportion of the mentee's
        available slots that are also available
        to the mentor.
        """

        mentor_availability = self._normalize(
            mentor.availability
        )

        mentee_availability = self._normalize(
            mentee.availability
        )

        if not mentee_availability:
            return 0.0

        overlap = (
            mentor_availability
            & mentee_availability
        )

        return (
            len(overlap)
            / len(mentee_availability)
        )