"""
feature_engineering — richer feature computation for mentor-mentee matching.

Public API
----------
Skill
    combined_skill_score     Jaccard + coverage weighted combination
    jaccard_skill_score      Jaccard similarity only
    skill_coverage_score     Mentee-perspective coverage only

Goal
    goal_alignment_score     TF-cosine semantic goal similarity

Experience / Industry / Availability
    experience_gap_score     Continuous score based on year-gap curve
    industry_match_score     Exact (1.0) or same-group (0.5) industry match
    availability_score       Slot overlap + timezone compatibility
    timezone_score           Timezone-difference score
    slot_overlap_score       Raw slot-overlap fraction
"""

from matching_engine.feature_engineering.skill_encoder import (
    combined_skill_score,
    jaccard_skill_score,
    skill_coverage_score,
)
from matching_engine.feature_engineering.goal_encoder import (
    goal_alignment_score,
)
from matching_engine.feature_engineering.feature_builder import (
    experience_gap_score,
    industry_match_score,
    availability_score,
    timezone_score,
    slot_overlap_score,
)

__all__ = [
    "combined_skill_score",
    "jaccard_skill_score",
    "skill_coverage_score",
    "goal_alignment_score",
    "experience_gap_score",
    "industry_match_score",
    "availability_score",
    "timezone_score",
    "slot_overlap_score",
]

