from __future__ import annotations

from matching_engine.models.mentor import Mentor
from matching_engine.models.mentee import Mentee
from matching_engine.models.match import Match

from matching_engine.optimization.candidate_generator import (
    CandidateGenerator,
)
from matching_engine.optimization.optimizer import (
    MatchingOptimizer,
    MatchAssignment,
)


class MatchingService:
    """
    High-level service for mentor-mentee matching.

    Pipeline:

        Mentors + Mentees
                ↓
        Candidate Generation
                ↓
        Match Scoring
                ↓
        Global Optimization
                ↓
        Match objects
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

    def match(
        self,
        mentors: list[Mentor],
        mentees: list[Mentee],
    ) -> list[Match]:
        """
        Generate globally optimized mentor-mentee matches.
        """

        if not mentors or not mentees:
            return []

        # -----------------------------------------------
        # 1. Generate candidate matches
        # -----------------------------------------------

        candidates_by_mentee = (
            self.candidate_generator.generate(
                mentors,
                mentees,
            )
        )

        if not candidates_by_mentee:
            return []

        # -----------------------------------------------
        # 2. Build mentor capacity map
        # -----------------------------------------------

        mentor_capacities = {
            mentor.id: mentor.available_capacity
            for mentor in mentors
        }

        # -----------------------------------------------
        # 3. Globally optimize candidates
        # -----------------------------------------------

        assignments = (
            self.optimizer.optimize_from_grouped_candidates(
                candidates_by_mentee,
                mentor_capacities,
            )
        )

        # -----------------------------------------------
        # 4. Convert assignments to Match objects
        # -----------------------------------------------

        return [
            self._to_match(assignment)
            for assignment in assignments
        ]

    @staticmethod
    def _to_match(
        assignment: MatchAssignment,
    ) -> Match:
        """
        Convert an optimizer assignment into the
        application's Match model.

        The Match model intentionally exposes individual
        scoring components rather than the raw feature
        dictionary.
        """

        features = assignment.features

        return Match(
            mentor_id=assignment.mentor_id,
            mentee_id=assignment.mentee_id,

            # Overall score
            score=round(
                assignment.score,
                4,
            ),

            # Current scoring components
            skill_score=round(
                features.get(
                    "skill_score",
                    0.0,
                ),
                4,
            ),

            experience_score=round(
                features.get(
                    "experience_score",
                    0.0,
                ),
                4,
            ),

            industry_score=round(
                features.get(
                    "industry_score",
                    0.0,
                ),
                4,
            ),

            availability_score=round(
                features.get(
                    "availability_score",
                    0.0,
                ),
                4,
            ),

            # These are not yet implemented by the
            # current scorer, so keep them at the
            # Match model default.
            goal_score=0.0,
            preference_score=0.0,

            is_valid=True,

            reasons=MatchingService._build_reasons(
                features,
            ),

            constraint_violations=[],
        )

    @staticmethod
    def _build_reasons(
        features: dict[str, float],
    ) -> list[str]:
        """
        Build human-readable explanations for a match.
        """

        reasons: list[str] = []

        skill_score = features.get(
            "skill_score",
            0.0,
        )

        expertise_score = features.get(
            "expertise_score",
            0.0,
        )

        industry_score = features.get(
            "industry_score",
            0.0,
        )

        experience_score = features.get(
            "experience_score",
            0.0,
        )

        availability_score = features.get(
            "availability_score",
            0.0,
        )

        topic_score = features.get(
            "topic_score",
            0.0,
        )

        if skill_score >= 1.0:
            reasons.append(
                "Strong skill alignment."
            )
        elif skill_score > 0.0:
            reasons.append(
                "Partial skill alignment."
            )

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
            reasons.append(
                "Industry preference is aligned."
            )

        if experience_score >= 1.0:
            reasons.append(
                "Experience levels are compatible."
            )

        if availability_score >= 1.0:
            reasons.append(
                "Availability is fully aligned."
            )
        elif availability_score > 0.0:
            reasons.append(
                "Availability partially overlaps."
            )

        if topic_score >= 1.0:
            reasons.append(
                "Mentoring topics align with "
                "the mentee's preferences."
            )

        return reasons