from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from matching_engine.models.mentor import Mentor
from matching_engine.models.mentee import Mentee
from matching_engine.scoring.scorer import MatchScorer


@dataclass(frozen=True)
class MatchCandidate:
    """
    Represents one possible mentor-mentee pairing.

    This is a candidate only. It does NOT mean that the
    mentor has been finally assigned to the mentee.

    The optimizer will make the final assignment later.
    """

    mentor_id: str
    mentee_id: str
    score: float
    features: dict[str, float]


class CandidateGenerator:
    """
    Generate and rank eligible mentor-mentee candidates.

    Responsibilities:
        1. Consider every mentor for every mentee.
        2. Apply basic eligibility checks.
        3. Calculate the compatibility score.
        4. Return multiple candidates for each mentee.
        5. Rank candidates from highest to lowest score.

    This class does NOT:
        - assign mentors permanently
        - update mentor capacity
        - solve the global optimization problem

    Those responsibilities belong to the optimizer.
    """

    def __init__(
        self,
        scorer: MatchScorer | None = None,
        minimum_score: float = 0.0,
    ) -> None:
        self.scorer = scorer or MatchScorer()
        self.minimum_score = minimum_score

    def generate(
        self,
        mentors: Iterable[Mentor],
        mentees: Iterable[Mentee],
    ) -> dict[str, list[MatchCandidate]]:
        """
        Generate candidates for every mentee.

        Returns:

            {
                "mentee-1": [
                    MatchCandidate(...),
                    MatchCandidate(...),
                ],
                "mentee-2": [
                    MatchCandidate(...),
                ],
            }

        Candidates for each mentee are sorted by descending
        compatibility score.
        """

        mentors = list(mentors)
        mentees = list(mentees)

        candidates_by_mentee: dict[
            str,
            list[MatchCandidate],
        ] = {}

        for mentee in mentees:
            candidates: list[MatchCandidate] = []

            for mentor in mentors:
                if not self._is_eligible(
                    mentor,
                    mentee,
                ):
                    continue

                features = self.scorer.score(
                    mentor,
                    mentee,
                )

                score = features["final_score"]

                if score < self.minimum_score:
                    continue

                candidates.append(
                    MatchCandidate(
                        mentor_id=mentor.id,
                        mentee_id=mentee.id,
                        score=score,
                        features=features,
                    )
                )

            candidates.sort(
                key=lambda candidate: candidate.score,
                reverse=True,
            )

            candidates_by_mentee[mentee.id] = candidates

        return candidates_by_mentee

    def generate_flat(
        self,
        mentors: Iterable[Mentor],
        mentees: Iterable[Mentee],
    ) -> list[MatchCandidate]:
        """
        Generate candidates as a flat list.

        Useful for optimization algorithms that expect
        a list of edges in a bipartite graph.
        """

        grouped = self.generate(
            mentors,
            mentees,
        )

        candidates: list[MatchCandidate] = []

        for mentee_candidates in grouped.values():
            candidates.extend(mentee_candidates)

        return candidates

    @staticmethod
    def _is_eligible(
        mentor: Mentor,
        mentee: Mentee,
    ) -> bool:
        """
        Apply hard eligibility constraints.

        Current hard constraints:

            1. Mentor must have available capacity.
            2. Mentor's preferred mentee experience levels,
               if specified, must include the mentee's level.
            3. Mentee's preferred mentor experience levels,
               if specified, must include the mentor's level.

        Soft compatibility factors such as skills,
        industry, availability and topics are handled
        by MatchScorer.
        """

        # ---------------------------------------------
        # Capacity
        # ---------------------------------------------

        if mentor.available_capacity <= 0:
            return False

        # ---------------------------------------------
        # Mentor's preferred mentee level
        # ---------------------------------------------

        if mentor.preferred_mentee_experience_levels:
            if not mentee.experience_level:
                return False

            preferred_levels = {
                level.strip().lower()
                for level
                in mentor.preferred_mentee_experience_levels
                if level and level.strip()
            }

            mentee_level = (
                mentee.experience_level.strip().lower()
            )

            if mentee_level not in preferred_levels:
                return False

        # ---------------------------------------------
        # Mentee's preferred mentor level
        # ---------------------------------------------

        if mentee.preferred_mentor_experience_levels:
            if not mentor.experience_level:
                return False

            preferred_levels = {
                level.strip().lower()
                for level
                in mentee.preferred_mentor_experience_levels
                if level and level.strip()
            }

            mentor_level = (
                mentor.experience_level.strip().lower()
            )

            if mentor_level not in preferred_levels:
                return False

        return True