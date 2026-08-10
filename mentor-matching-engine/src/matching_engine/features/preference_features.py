
from __future__ import annotations

from matching_engine.models.mentor import Mentor
from matching_engine.models.mentee import Mentee


class PreferenceFeatureExtractor:
    """
    Extract preference-based compatibility features between
    a mentor and mentee.

    The mentee's preferences are compared against the
    mentor's profile:

        - preferred_industries
        - preferred_mentor_experience_levels
        - preferred_mentor_topics

    Returns explainable numerical features that can later
    be combined by MatchScorer.
    """

    def extract(
        self,
        mentor: Mentor,
        mentee: Mentee,
    ) -> dict[str, float]:
        """
        Calculate preference compatibility features.

        Returns:
            Dictionary containing:

                preference_score
                industry_preference_score
                experience_preference_score
                topic_preference_score
        """

        industry_score = self._industry_preference(
            mentor,
            mentee,
        )

        experience_score = self._experience_preference(
            mentor,
            mentee,
        )

        topic_score = self._topic_preference(
            mentor,
            mentee,
        )

        applicable_scores = []

        if mentee.preferred_industries:
            applicable_scores.append(industry_score)

        if mentee.preferred_mentor_experience_levels:
            applicable_scores.append(experience_score)

        if mentee.preferred_mentor_topics:
            applicable_scores.append(topic_score)

        if applicable_scores:
            preference_score = (
                sum(applicable_scores)
                / len(applicable_scores)
            )
        else:
            preference_score = 0.0

        return {
            "preference_score": round(
                preference_score,
                4,
            ),
            "industry_preference_score": round(
                industry_score,
                4,
            ),
            "experience_preference_score": round(
                experience_score,
                4,
            ),
            "topic_preference_score": round(
                topic_score,
                4,
            ),
        }

    @staticmethod
    def _industry_preference(
        mentor: Mentor,
        mentee: Mentee,
    ) -> float:
        """
        Compare the mentor's industry with the
        mentee's preferred industries.

        Returns 1.0 when the mentor's industry is
        explicitly preferred, otherwise 0.0.
        """

        preferences = {
            value.strip().lower()
            for value in mentee.preferred_industries
            if value and value.strip()
        }

        if not preferences:
            return 0.0

        if not mentor.industry:
            return 0.0

        return (
            1.0
            if mentor.industry.strip().lower()
            in preferences
            else 0.0
        )

    @staticmethod
    def _experience_preference(
        mentor: Mentor,
        mentee: Mentee,
    ) -> float:
        """
        Compare the mentor's experience level with the
        mentee's preferred mentor experience levels.

        Returns 1.0 when the mentor's experience level
        is explicitly preferred, otherwise 0.0.
        """

        preferences = {
            value.strip().lower()
            for value in mentee.preferred_mentor_experience_levels
            if value and value.strip()
        }

        if not preferences:
            return 0.0

        if not mentor.experience_level:
            return 0.0

        return (
            1.0
            if mentor.experience_level.strip().lower()
            in preferences
            else 0.0
        )

    @staticmethod
    def _topic_preference(
        mentor: Mentor,
        mentee: Mentee,
    ) -> float:
        """
        Compare the mentee's preferred mentor topics
        with the mentor's mentoring topics.

        The score is the proportion of preferred topics
        that the mentor can provide.
        """

        preferences = {
            value.strip().lower()
            for value in mentee.preferred_mentor_topics
            if value and value.strip()
        }

        topics = {
            value.strip().lower()
            for value in mentor.mentoring_topics
            if value and value.strip()
        }

        if not preferences:
            return 0.0

        if not topics:
            return 0.0

        overlap = preferences.intersection(topics)

        return len(overlap) / len(preferences)
