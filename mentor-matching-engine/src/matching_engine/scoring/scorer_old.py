
from __future__ import annotations

from matching_engine.features.skill_features import (
    SkillFeatureExtractor,
)
from matching_engine.models.mentor import Mentor
from matching_engine.models.mentee import Mentee


class MatchScorer:
    """
    Calculate an overall compatibility score between
    a mentor and a mentee.

    Scoring weights:

        Skill / capability coverage : 40%
        Expertise match             : 20%
        Industry match              : 15%
        Experience fit              : 10%
        Availability                : 10%
        Mentoring topics            : 5%

    Total                           : 100%
    """

    SKILL_WEIGHT = 0.40
    EXPERTISE_WEIGHT = 0.20
    INDUSTRY_WEIGHT = 0.15
    EXPERIENCE_WEIGHT = 0.10
    AVAILABILITY_WEIGHT = 0.10
    TOPIC_WEIGHT = 0.05

    def __init__(self) -> None:
        self.skill_extractor = SkillFeatureExtractor()

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
        # 1. Skill / capability score
        # -------------------------------------------------
        skill_features = self.skill_extractor.extract(
            mentor,
            mentee,
        )

        skill_score = skill_features["skill_coverage"]

        # -------------------------------------------------
        # 2. Expertise score
        #
        # Mentor expertise + skills + mentoring topics
        # are treated as mentor capabilities.
        # -------------------------------------------------
        mentor_capabilities = self._mentor_capabilities(
            mentor
        )

        mentee_learning = self._mentee_learning_targets(
            mentee
        )

        expertise_score = self._list_match_score(
            mentor_capabilities,
            mentee_learning,
        )

        # -------------------------------------------------
        # 3. Industry score
        # -------------------------------------------------
        industry_score = self._industry_score(
            mentor,
            mentee,
        )

        # -------------------------------------------------
        # 4. Experience score
        # -------------------------------------------------
        experience_score = self._experience_score(
            mentor,
            mentee,
        )

        # -------------------------------------------------
        # 5. Availability score
        # -------------------------------------------------
        availability_score = self._availability_score(
            mentor,
            mentee,
        )

        # -------------------------------------------------
        # 6. Mentoring topic score
        # -------------------------------------------------
        topic_score = self._list_match_score(
            mentor.mentoring_topics,
            mentee.preferred_mentor_topics,
        )

        # -------------------------------------------------
        # Final weighted score
        # -------------------------------------------------
        final_score = (
            skill_score * self.SKILL_WEIGHT
            + expertise_score * self.EXPERTISE_WEIGHT
            + industry_score * self.INDUSTRY_WEIGHT
            + experience_score * self.EXPERIENCE_WEIGHT
            + availability_score * self.AVAILABILITY_WEIGHT
            + topic_score * self.TOPIC_WEIGHT
        )

        return {
            "skill_score": round(
                skill_score,
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
            "topic_score": round(
                topic_score,
                4,
            ),
            "final_score": round(
                final_score,
                4,
            ),
        }

    # =====================================================
    # Mentor capabilities
    # =====================================================

    @classmethod
    def _mentor_capabilities(
        cls,
        mentor: Mentor,
    ) -> list[str]:
        """
        Build the complete set of capabilities a mentor
        can potentially provide.

        Capabilities come from:

            - mentor.skills
            - mentor.expertise
            - mentor.mentoring_topics
        """

        capabilities = (
            list(mentor.skills)
            + list(mentor.expertise)
            + list(mentor.mentoring_topics)
        )

        return list(
            cls._normalize(capabilities)
        )

    @classmethod
    def _mentee_learning_targets(
        cls,
        mentee: Mentee,
    ) -> list[str]:
        """
        Determine what the mentee wants to learn.

        Primary source:
            skills_to_learn

        Fallback:
            interests

        This prevents an empty skills_to_learn list from
        producing no meaningful capability comparison.
        """

        learning_targets = mentee.skills_to_learn

        if not learning_targets:
            learning_targets = mentee.interests

        return list(
            cls._normalize(learning_targets)
        )

    # =====================================================
    # Normalization
    # =====================================================

    @staticmethod
    def _normalize(
        values: list[str],
    ) -> set[str]:
        """
        Normalize values for case-insensitive comparison.

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

    # =====================================================
    # List matching
    # =====================================================

    @classmethod
    def _list_match_score(
        cls,
        mentor_values: list[str],
        mentee_values: list[str],
    ) -> float:
        """
        Calculate the proportion of mentee requirements
        supported by the mentor.

        Example:

            Mentor:
                Python
                Machine Learning
                AWS

            Mentee:
                Python
                Machine Learning
                Kubernetes

            Score:

                2 / 3 = 0.6667
        """

        mentor_set = cls._normalize(
            mentor_values
        )

        mentee_set = cls._normalize(
            mentee_values
        )

        if not mentee_set:
            return 0.0

        overlap = mentor_set.intersection(
            mentee_set
        )

        return len(overlap) / len(
            mentee_set
        )

    # =====================================================
    # Industry
    # =====================================================

    @classmethod
    def _industry_score(
        cls,
        mentor: Mentor,
        mentee: Mentee,
    ) -> float:
        """
        Calculate industry compatibility.

        Exact mentor/mentee industry match:
            1.0

        Mentee industry appears in mentor's
        preferred industries:
            1.0

        Otherwise:
            0.0
        """

        if not mentor.industry or not mentee.industry:
            return 0.0

        mentor_industry = (
            mentor.industry.strip().lower()
        )

        mentee_industry = (
            mentee.industry.strip().lower()
        )

        if mentor_industry == mentee_industry:
            return 1.0

        preferred = cls._normalize(
            mentor.preferred_industries
        )

        if mentee_industry in preferred:
            return 1.0

        return 0.0

    # =====================================================
    # Experience
    # =====================================================

    @staticmethod
    def _experience_score(
        mentor: Mentor,
        mentee: Mentee,
    ) -> float:
        """
        Calculate experience compatibility.

        A mentor at or above the mentee's experience
        level receives 1.0.

        A mentor below the mentee's level receives 0.5.

        If explicit levels are unavailable, years of
        experience are used as a fallback.
        """

        if (
            mentor.experience_level
            and mentee.experience_level
        ):
            levels = {
                "beginner": 1,
                "junior": 2,
                "intermediate": 3,
                "mid": 3,
                "mid-level": 3,
                "senior": 4,
                "advanced": 4,
                "expert": 5,
            }

            mentor_level = levels.get(
                mentor.experience_level.strip().lower()
            )

            mentee_level = levels.get(
                mentee.experience_level.strip().lower()
            )

            if (
                mentor_level is not None
                and mentee_level is not None
            ):
                if mentor_level >= mentee_level:
                    return 1.0

                return 0.5

        # Fallback to years of experience.
        if (
            mentor.years_experience
            >= mentee.years_experience
        ):
            return 1.0

        if mentor.years_experience > 0:
            return 0.5

        return 0.0

    # =====================================================
    # Availability
    # =====================================================

    @classmethod
    def _availability_score(
        cls,
        mentor: Mentor,
        mentee: Mentee,
    ) -> float:
        """
        Calculate availability compatibility.

        Score:

            overlapping slots
            -----------------
            mentee availability

        Example:

            Mentor:
                Monday
                Wednesday

            Mentee:
                Monday
                Friday

            Score:

                1 / 2 = 0.5
        """

        mentor_availability = cls._normalize(
            mentor.availability
        )

        mentee_availability = cls._normalize(
            mentee.availability
        )

        if (
            not mentor_availability
            or not mentee_availability
        ):
            return 0.0

        overlap = mentor_availability.intersection(
            mentee_availability
        )

        return len(overlap) / len(
            mentee_availability
        )
