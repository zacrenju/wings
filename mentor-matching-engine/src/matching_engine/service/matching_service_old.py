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
from matching_engine.constraints.validator import (
    MatchingConstraintValidator,
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
        validator: MatchingConstraintValidator | None = None,
    ) -> None:

        self.candidate_generator = (
            candidate_generator
            or CandidateGenerator()
        )

        self.optimizer = (
            optimizer
            or MatchingOptimizer()
        )
        self.validator = (
        validator
        or MatchingConstraintValidator()
    )

    def match(
        self,
        mentors: list[Mentor],
        mentees: list[Mentee],
    ) -> list[Match]:
        """
    Generate globally optimized mentor-mentee matches.

    Hard constraints are checked before candidate generation.
    """

        if not mentors or not mentees:
            return []

    # -------------------------------------------------
    # 1. Validate mentor-mentee pairs
    # -------------------------------------------------

        valid_mentors_by_mentee: dict[str, list[Mentor]] = {}

        for mentee in mentees:
            valid_mentors: list[Mentor] = []

            for mentor in mentors:
                validation = self.validator.validate(
                mentor,
                mentee,
            )

                if validation.is_valid:
                    valid_mentors.append(mentor)

            if valid_mentors:
                    valid_mentors_by_mentee[mentee.id] = valid_mentors

        if not valid_mentors_by_mentee:
                    return []

    # -------------------------------------------------
    # 2. Generate candidates only for valid pairs
    # -------------------------------------------------

        candidates_by_mentee: dict[str, list] = {}

        for mentee in mentees:
           valid_mentors = valid_mentors_by_mentee.get(
            mentee.id,
            [],
        )

           if not valid_mentors:
             continue

           generated = self.candidate_generator.generate(
            valid_mentors,
            [mentee],
        )

           candidates_by_mentee.update(generated)

        if not candidates_by_mentee:
          return []

    # -------------------------------------------------
    # 3. Build mentor capacity map
    # -------------------------------------------------

        mentor_capacities = {
           mentor.id: mentor.available_capacity
           for mentor in mentors
         }

    # -------------------------------------------------
    # 4. Global optimization
    # -------------------------------------------------

        assignments = (
            self.optimizer.optimize_from_grouped_candidates(
            candidates_by_mentee,
            mentor_capacities,
        )
        )

    # -------------------------------------------------
    # 5. Convert assignments to Match objects
    # -------------------------------------------------

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