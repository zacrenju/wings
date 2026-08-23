from __future__ import annotations

from matching_engine.models.mentor import Mentor
from matching_engine.models.mentee import Mentee
from matching_engine.models.match import Match

from matching_engine.optimization.candidate_generator import (
    CandidateGenerator,
    MatchCandidate,
)
from matching_engine.optimization.optimizer import (
    MatchingOptimizer,
    MatchAssignment,
)


class MatchingService:
    """
    High-level service for mentor-mentee matching.

    Two entry points:

        match()      — globally optimized 1-to-1 assignments
        recommend()  — top-k ranked mentor suggestions per mentee
                       (no capacity enforcement, useful for UIs /
                        exploration before a final assignment run)

    Pipeline for match():

        Mentors + Mentees
                ↓
        Candidate Generation
                ↓
        Match Scoring
                ↓
        Global Optimization
                ↓
        Match objects

    Pipeline for recommend():

        Mentors + Mentees
                ↓
        Candidate Generation  (scoring only)
                ↓
        Top-k selection per mentee
                ↓
        {mentee_id: [Match, …]}
    """

    def __init__(
        self,
        candidate_generator: CandidateGenerator | None = None,
        optimizer: MatchingOptimizer | None = None,
    ) -> None:

        self.candidate_generator = (
            candidate_generator
            or CandidateGenerator()
        )

        self.optimizer = (
            optimizer
            or MatchingOptimizer()
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def match(
        self,
        mentors: list[Mentor],
        mentees: list[Mentee],
    ) -> list[Match]:
        """
        Generate globally optimized mentor-mentee matches.

        Respects mentor capacity constraints and maximises the
        total compatibility score across all assignments.

        Returns:
            One Match per mentee that could be assigned a mentor,
            sorted by descending score.
        """

        if not mentors or not mentees:
            return []

        candidates_by_mentee = self.candidate_generator.generate(
            mentors,
            mentees,
        )

        if not candidates_by_mentee:
            return []

        mentor_capacities = {
            mentor.id: mentor.available_capacity
            for mentor in mentors
        }

        assignments = self.optimizer.optimize_from_grouped_candidates(
            candidates_by_mentee,
            mentor_capacities,
        )

        return [
            self._assignment_to_match(assignment)
            for assignment in assignments
        ]

    def recommend(
        self,
        mentors: list[Mentor],
        mentees: list[Mentee],
        top_k: int = 3,
    ) -> dict[str, list[Match]]:
        """
        Return the top-k mentor recommendations for each mentee.

        Unlike match(), this method does NOT run global optimization
        or enforce capacity constraints.  It scores every eligible
        mentor for each mentee independently and returns the k
        highest-scoring options.  This is useful for showing ranked
        suggestions to a mentee before a final assignment is made.

        Args:
            mentors: Pool of available mentors.
            mentees: Pool of mentees seeking recommendations.
            top_k:   Maximum number of mentor recommendations to
                     return per mentee (default 3).

        Returns:
            A dict mapping each mentee's id to a list of up to
            top_k Match objects, ordered by descending score::

                {
                    "mentee-1": [Match(score=0.92), Match(score=0.81), …],
                    "mentee-2": [Match(score=0.78), …],
                }

            Mentees with no eligible mentors are omitted from the dict.
        """
        if not mentors or not mentees or top_k < 1:
            return {}

        candidates_by_mentee = self.candidate_generator.generate(
            mentors,
            mentees,
        )

        recommendations: dict[str, list[Match]] = {}

        for mentee_id, candidates in candidates_by_mentee.items():
            top_candidates = candidates[:top_k]
            if top_candidates:
                recommendations[mentee_id] = [
                    self._candidate_to_match(c)
                    for c in top_candidates
                ]

        return recommendations

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_match(
        mentor_id: str,
        mentee_id: str,
        score: float,
        features: dict[str, float],
    ) -> Match:
        """
        Core factory — builds a Match from raw scoring artefacts.
        """
        return Match(
            mentor_id=mentor_id,
            mentee_id=mentee_id,
            score=round(score, 4),
            skill_score=round(features.get("skill_score", 0.0), 4),
            goal_score=round(features.get("goal_score", 0.0), 4),
            expertise_score=round(features.get("expertise_score", 0.0), 4),
            experience_score=round(features.get("experience_score", 0.0), 4),
            industry_score=round(features.get("industry_score", 0.0), 4),
            availability_score=round(features.get("availability_score", 0.0), 4),
            preference_score=round(features.get("preference_score", 0.0), 4),
            is_valid=True,
            reasons=MatchingService._build_reasons(features),
            constraint_violations=[],
        )

    @staticmethod
    def _assignment_to_match(assignment: MatchAssignment) -> Match:
        return MatchingService._build_match(
            mentor_id=assignment.mentor_id,
            mentee_id=assignment.mentee_id,
            score=assignment.score,
            features=assignment.features,
        )

    @staticmethod
    def _candidate_to_match(candidate: MatchCandidate) -> Match:
        return MatchingService._build_match(
            mentor_id=candidate.mentor_id,
            mentee_id=candidate.mentee_id,
            score=candidate.score,
            features=candidate.features,
        )

    @staticmethod
    def _build_reasons(features: dict[str, float]) -> list[str]:
        """Build human-readable explanations for a match."""

        reasons: list[str] = []

        skill_score        = features.get("skill_score", 0.0)
        expertise_score    = features.get("expertise_score", 0.0)
        industry_score     = features.get("industry_score", 0.0)
        experience_score   = features.get("experience_score", 0.0)
        availability_score = features.get("availability_score", 0.0)
        topic_score        = features.get("topic_score", 0.0)

        if skill_score >= 1.0:
            reasons.append("Strong skill alignment.")
        elif skill_score > 0.0:
            reasons.append("Partial skill alignment.")

        if expertise_score >= 1.0:
            reasons.append(
                "Mentor expertise aligns with the mentee's learning needs."
            )
        elif expertise_score > 0.0:
            reasons.append(
                "Some mentor expertise aligns with the mentee's learning needs."
            )

        if industry_score >= 1.0:
            reasons.append("Industry preference is aligned.")
        elif industry_score > 0.0:
            reasons.append("Partial industry alignment.")

        if experience_score >= 1.0:
            reasons.append("Experience levels are compatible.")

        if availability_score >= 1.0:
            reasons.append("Availability is fully aligned.")
        elif availability_score > 0.0:
            reasons.append("Availability partially overlaps.")

        if topic_score >= 1.0:
            reasons.append("Mentoring topics align with the mentee's preferences.")

        return reasons