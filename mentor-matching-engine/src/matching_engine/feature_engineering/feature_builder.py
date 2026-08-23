"""
Feature builders for experience gap, industry matching, and availability overlap.
"""
from __future__ import annotations

from matching_engine.feature_engineering.constants import (
    INDUSTRY_GROUPS,
    MAX_COMPATIBLE_TZ_DIFF_HOURS,
    MIN_EXPERIENCE_GAP_YEARS,
    OPTIMAL_EXPERIENCE_GAP_YEARS,
    TIMEZONE_UTC_OFFSETS,
)
from matching_engine.models.mentee import Mentee
from matching_engine.models.mentor import Mentor


# --------------------------------------------------------------------------- #
# Experience score
# --------------------------------------------------------------------------- #

def experience_gap_score(mentor: Mentor, mentee: Mentee) -> float:
    """
    Score based on the years-of-experience gap between mentor and mentee.

    - Gap < MIN_EXPERIENCE_GAP_YEARS       → 0.0  (too small, not enough seniority)
    - Gap == OPTIMAL_EXPERIENCE_GAP_YEARS  → 1.0
    - Gap > OPTIMAL_EXPERIENCE_GAP_YEARS   → slowly decreasing (still valid but
                                              very senior mentors may have gaps)
    Returns float in [0.0, 1.0].
    """
    gap = mentor.years_experience - mentee.years_experience

    if gap < MIN_EXPERIENCE_GAP_YEARS:
        return 0.0

    if gap <= OPTIMAL_EXPERIENCE_GAP_YEARS:
        # Linear ramp from MIN_GAP → OPTIMAL_GAP
        return round(
            (gap - MIN_EXPERIENCE_GAP_YEARS) / (OPTIMAL_EXPERIENCE_GAP_YEARS - MIN_EXPERIENCE_GAP_YEARS),
            6,
        )

    # Beyond optimal — diminishing returns (capped at 1.0, but penalise very large gaps slightly)
    excess = gap - OPTIMAL_EXPERIENCE_GAP_YEARS
    penalty = min(0.3, excess * 0.02)   # At most 30% penalty for very large gaps
    return round(max(0.0, 1.0 - penalty), 6)


# --------------------------------------------------------------------------- #
# Industry score
# --------------------------------------------------------------------------- #

def _find_industry_group(industry: str) -> str | None:
    industry_lower = industry.strip().lower()
    for group, members in INDUSTRY_GROUPS.items():
        if any(member in industry_lower or industry_lower in member for member in members):
            return group
    return None


def industry_match_score(mentor: Mentor, mentee: Mentee) -> float:
    """
    Score based on industry / domain alignment.

    - Exact match (normalised)          → 1.0
    - Same industry group               → 0.5
    - Different industry groups         → 0.0

    Returns float in {0.0, 0.5, 1.0}.
    """
    if not mentor.industry or not mentee.industry:
        return 0.0

    m_ind = mentor.industry.strip().lower()
    mt_ind = mentee.industry.strip().lower()

    if m_ind == mt_ind:
        return 1.0

    m_group = _find_industry_group(m_ind)
    mt_group = _find_industry_group(mt_ind)

    if m_group and mt_group and m_group == mt_group:
        return 0.5

    return 0.0


# --------------------------------------------------------------------------- #
# Availability / timezone score
# --------------------------------------------------------------------------- #

def _tz_offset(tz: str) -> int | None:
    return TIMEZONE_UTC_OFFSETS.get(tz.strip().upper())


def timezone_score(mentor_tz: str, mentee_tz: str) -> float:
    """
    Score based on timezone difference.

    - Same timezone (diff = 0)           → 1.0
    - diff <= 3 hours                    → 0.75
    - diff <= MAX_COMPATIBLE_TZ_DIFF     → 0.5
    - diff >  MAX_COMPATIBLE_TZ_DIFF     → 0.0
    """
    m_offset = _tz_offset(mentor_tz)
    mt_offset = _tz_offset(mentee_tz)

    if m_offset is None or mt_offset is None:
        return 0.5   # Unknown timezone — assume neutral

    diff = abs(m_offset - mt_offset)
    if diff == 0:
        return 1.0
    if diff <= 3:
        return 0.75
    if diff <= MAX_COMPATIBLE_TZ_DIFF_HOURS:
        return 0.5
    return 0.0


def slot_overlap_score(mentor_slots: list[str], mentee_slots: list[str]) -> float:
    """
    Fraction of mentee's requested slots that the mentor also offers.

    Returns float in [0.0, 1.0].
    """
    if not mentor_slots or not mentee_slots:
        return 0.0
    m_set = {s.strip().lower() for s in mentor_slots}
    mt_set = {s.strip().lower() for s in mentee_slots}
    overlap = m_set & mt_set
    return round(len(overlap) / len(mt_set), 6)


def availability_score(mentor: Mentor, mentee: Mentee) -> float:
    """
    Combined availability score = 0.6 * slot_overlap + 0.4 * timezone_score.
    """
    mentor_tz = mentor.timezone or ""
    mentee_tz = mentee.timezone or ""
    tz = timezone_score(mentor_tz, mentee_tz)
    slots = slot_overlap_score(mentor.availability, mentee.availability)
    return round(0.4 * tz + 0.6 * slots, 6)
