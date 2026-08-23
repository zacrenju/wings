from __future__ import annotations

from matching_engine.models.match import Match
from matching_engine.optimization.optimizer import MatchAssignment


class MatchBuilder:
    """Build application Match objects from optimizer assignments."""

    @staticmethod
    def build(assignment: MatchAssignment) -> Match:
        features = assignment.features

        return Match(
            mentor_id=assignment.mentor_id,
            mentee_id=assignment.mentee_id,
            score=round(assignment.score, 4),

            skill_score=round(
                features.get("skill_score", 0.0),
                4,
            ),
            goal_score=round(
                features.get("goal_score", 0.0),
                4,
            ),
            experience_score=round(
                features.get("experience_score", 0.0),
                4,
            ),
            industry_score=round(
                features.get("industry_score", 0.0),
                4,
            ),
            availability_score=round(
                features.get("availability_score", 0.0),
                4,
            ),
            preference_score=round(
                features.get("preference_score", 0.0),
                4,
            ),

            is_valid=True,

            reasons=MatchBuilder.build_reasons(features),

            constraint_violations=[],
        )

    @staticmethod
    def build_reasons(
        features: dict[str, float],
    ) -> list[str]:

        reasons: list[str] = []

        skill_score = features.get("skill_score", 0.0)
        expertise_score = features.get("expertise_score", 0.0)
        industry_score = features.get("industry_score", 0.0)
        experience_score = features.get("experience_score", 0.0)
        availability_score = features.get("availability_score", 0.0)
        topic_score = features.get("topic_score", 0.0)

        if skill_score >= 1.0:
            reasons.append("Strong skill alignment.")
        elif skill_score > 0.0:
            reasons.append("Partial skill alignment.")

        if expertise_score >= 1.0:
            reasons.append(
                "Mentor expertise aligns with "
                "the mentee's learning needs."
            )
        elif expertise_score > 0.0:
            reasons.append(
                "Some mentor expertise aligns "
                "with the mentee's learning needs."
            )

        if industry_score >= 1.0:
            reasons.append("Industry preference is aligned.")

        if experience_score >= 1.0:
            reasons.append("Experience levels are compatible.")

        if availability_score >= 1.0:
            reasons.append("Availability is fully aligned.")
        elif availability_score > 0.0:
            reasons.append("Availability partially overlaps.")

        if topic_score >= 1.0:
            reasons.append(
                "Mentoring topics align with "
                "the mentee's preferences."
            )

        return reasons