
from __future__ import annotations

from matching_engine.models.mentor import Mentor
from matching_engine.models.mentee import Mentee


class SkillFeatureExtractor:
    """
    Extract skill-based compatibility features between
    a mentor and a mentee.

    Mentor capabilities are derived from:
        - skills
        - expertise
        - mentoring_topics

    Mentee learning requirements are derived primarily from:
        - skills_to_learn

    If skills_to_learn is empty, interests are used
    as a fallback.
    """

    def extract(
        self,
        mentor: Mentor,
        mentee: Mentee,
    ) -> dict[str, float]:
        """
        Calculate skill compatibility features.

        Returns:
            Dictionary containing explainable numerical
            skill compatibility features.
        """

        # -------------------------------------------------
        # Mentor capabilities
        # -------------------------------------------------

        mentor_capabilities = (
            self._build_mentor_capabilities(mentor)
        )

        # -------------------------------------------------
        # Mentee learning requirements
        # -------------------------------------------------

        skills_to_learn = self._normalize(
            mentee.skills_to_learn
        )

        # If the mentee has not specified skills to learn,
        # use interests as a fallback.
        if not skills_to_learn:
            skills_to_learn = self._normalize(
                mentee.interests
            )

        # -------------------------------------------------
        # No learning requirements
        # -------------------------------------------------

        if not skills_to_learn:
            return {
                "skill_overlap": 0.0,
                "skill_coverage": 0.0,
                "missing_skills": 0.0,
                "mentor_skill_count": float(
                    len(mentor_capabilities)
                ),
                "mentee_skill_count": 0.0,
            }

        # -------------------------------------------------
        # Matching
        # -------------------------------------------------

        matched_skills = (
            mentor_capabilities.intersection(
                skills_to_learn
            )
        )

        missing_skills = (
            skills_to_learn - mentor_capabilities
        )

        # Percentage of the mentee's requested
        # skills that the mentor can support.
        skill_coverage = (
            len(matched_skills)
            / len(skills_to_learn)
        )

        return {
            "skill_overlap": round(
                skill_coverage,
                4,
            ),
            "skill_coverage": round(
                skill_coverage,
                4,
            ),
            "missing_skills": float(
                len(missing_skills)
            ),
            "mentor_skill_count": float(
                len(mentor_capabilities)
            ),
            "mentee_skill_count": float(
                len(skills_to_learn)
            ),
        }

    @classmethod
    def _build_mentor_capabilities(
        cls,
        mentor: Mentor,
    ) -> set[str]:
        """
        Build the complete set of capabilities
        that the mentor can potentially provide.

        Sources:
            - skills
            - expertise
            - mentoring_topics
        """

        capabilities: set[str] = set()

        capabilities.update(
            cls._normalize(mentor.skills)
        )

        capabilities.update(
            cls._normalize(mentor.expertise)
        )

        capabilities.update(
            cls._normalize(mentor.mentoring_topics)
        )

        return capabilities

    @staticmethod
    def _normalize(
        values: list[str],
    ) -> set[str]:
        """
        Normalize values for reliable comparison.

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
=================

from __future__ import annotations

from matching_engine.models.mentor import Mentor
from matching_engine.models.mentee import Mentee


class SkillFeatureExtractor:
    """
    Extract skill-based compatibility features between
    a mentor and a mentee.

    Mentor capabilities are derived from:
        - skills
        - expertise
        - mentoring_topics

    Mentee learning requirements are derived primarily from:
        - skills_to_learn

    If skills_to_learn is empty, interests are used
    as a fallback.
    """

    def extract(
        self,
        mentor: Mentor,
        mentee: Mentee,
    ) -> dict[str, float]:
        """
        Calculate skill compatibility features.

        Returns:
            Dictionary containing explainable numerical
            skill compatibility features.
        """

        # -------------------------------------------------
        # Mentor capabilities
        # -------------------------------------------------

        mentor_capabilities = (
            self._build_mentor_capabilities(mentor)
        )

        # -------------------------------------------------
        # Mentee learning requirements
        # -------------------------------------------------

        skills_to_learn = self._normalize(
            mentee.skills_to_learn
        )

        # If the mentee has not specified skills to learn,
        # use interests as a fallback.
        if not skills_to_learn:
            skills_to_learn = self._normalize(
                mentee.interests
            )

        # -------------------------------------------------
        # No learning requirements
        # -------------------------------------------------

        if not skills_to_learn:
            return {
                "skill_score": 0.0,
                "skill_overlap": 0.0,
                "skill_coverage": 0.0,
                "missing_skills": 0.0,
                "mentor_skill_count": float(
                    len(mentor_capabilities)
                ),
                "mentee_skill_count": 0.0,
            }

        # -------------------------------------------------
        # Matching
        # -------------------------------------------------

        matched_skills = (
            mentor_capabilities.intersection(
                skills_to_learn
            )
        )

        missing_skills = (
            skills_to_learn - mentor_capabilities
        )

        # Percentage of the mentee's requested
        # skills that the mentor can support.
        skill_coverage = (
            len(matched_skills)
            / len(skills_to_learn)
        )

        # skill_score is the primary score consumed
        # by MatchScorer.
        skill_score = skill_coverage

        return {
            "skill_score": round(
                skill_score,
                4,
            ),
            "skill_overlap": round(
                skill_coverage,
                4,
            ),
            "skill_coverage": round(
                skill_coverage,
                4,
            ),
            "missing_skills": float(
                len(missing_skills)
            ),
            "mentor_skill_count": float(
                len(mentor_capabilities)
            ),
            "mentee_skill_count": float(
                len(skills_to_learn)
            ),
        }

    @classmethod
    def _build_mentor_capabilities(
        cls,
        mentor: Mentor,
    ) -> set[str]:
        """
        Build the mentor's explicit skill set.

        Only the mentor's declared skills are used here.
        Expertise and mentoring topics are evaluated
        separately by other scoring features.
        """

        return cls._normalize(
         mentor.skills
    )
    
    @staticmethod
    def _normalize(
        values: list[str],
    ) -> set[str]:
        """
        Normalize values for reliable comparison.

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