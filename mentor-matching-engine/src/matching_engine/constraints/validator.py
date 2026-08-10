from dataclasses import dataclass, field

from matching_engine.models import Mentor, Mentee


@dataclass
class ConstraintResult:
    """Result of validating a mentor-mentee pair."""

    is_valid: bool
    violations: list[str] = field(default_factory=list)

    @property
    def reasons(self) -> list[str]:
        """Return the constraint validation reasons."""
        if self.is_valid:
            return ["All hard constraints satisfied."]
        return self.violations


class MatchingConstraintValidator:
    """
    Validate hard constraints between a mentor and mentee.

    Hard constraints determine whether a mentor-mentee pair is eligible
    for further scoring.

    This class does NOT calculate compatibility scores.
    """

    def validate(
        self,
        mentor: Mentor,
        mentee: Mentee,
    ) -> ConstraintResult:
        """
        Validate a mentor-mentee pair.

        Returns:
            ConstraintResult indicating whether the pair is eligible.
        """

        violations: list[str] = []

        self._check_capacity(
            mentor=mentor,
            violations=violations,
        )

        self._check_availability(
            mentor=mentor,
            mentee=mentee,
            violations=violations,
        )

        self._check_experience_preference(
            mentor=mentor,
            mentee=mentee,
            violations=violations,
        )

        self._check_industry_preference(
            mentor=mentor,
            mentee=mentee,
            violations=violations,
        )

        return ConstraintResult(
            is_valid=len(violations) == 0,
            violations=violations,
        )

    @staticmethod
    def _check_capacity(
        mentor: Mentor,
        violations: list[str],
    ) -> None:
        """Check whether the mentor has capacity for another mentee."""

        if mentor.available_capacity <= 0:
            violations.append(
                f"Mentor {mentor.id} has no available capacity."
            )

    @staticmethod
    def _check_availability(
        mentor: Mentor,
        mentee: Mentee,
        violations: list[str],
    ) -> None:
        """
        Check whether mentor and mentee have overlapping availability.

        If either profile does not specify availability, we do not reject
        the pair. The missing information can be handled later.
        """

        if not mentor.availability or not mentee.availability:
            return

        mentor_slots = {
            slot.strip().lower()
            for slot in mentor.availability
        }

        mentee_slots = {
            slot.strip().lower()
            for slot in mentee.availability
        }

        if not mentor_slots.intersection(mentee_slots):
            violations.append(
                "Mentor and mentee have no overlapping availability."
            )

    @staticmethod
    def _check_experience_preference(
        mentor: Mentor,
        mentee: Mentee,
        violations: list[str],
    ) -> None:
        """
        Check whether the mentee's experience level is acceptable
        to the mentor.

        An empty preference list means no restriction.
        """

        if not mentor.preferred_mentee_experience_levels:
            return

        if not mentee.experience_level:
            return

        allowed_levels = {
            level.strip().lower()
            for level in mentor.preferred_mentee_experience_levels
        }

        mentee_level = mentee.experience_level.strip().lower()

        if mentee_level not in allowed_levels:
            violations.append(
                f"Mentee experience level '{mentee.experience_level}' "
                f"is not preferred by mentor {mentor.id}."
            )

    @staticmethod
    def _check_industry_preference(
        mentor: Mentor,
        mentee: Mentee,
        violations: list[str],
    ) -> None:
        """
        Check whether the mentee's industry is acceptable to the mentor.

        An empty preference list means no restriction.
        """

        if not mentor.preferred_industries:
            return

        if not mentee.industry:
            return

        preferred_industries = {
            industry.strip().lower()
            for industry in mentor.preferred_industries
        }

        mentee_industry = mentee.industry.strip().lower()

        if mentee_industry not in preferred_industries:
            violations.append(
                f"Mentee industry '{mentee.industry}' "
                f"is not preferred by mentor {mentor.id}."
            )