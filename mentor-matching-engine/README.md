# Mentor Matching Engine

A Python library that intelligently pairs mentors with mentees by scoring compatibility across multiple dimensions and running a global optimization to produce the best possible set of matches.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Models](#models)
- [Scoring Dimensions](#scoring-dimensions)
- [Feature Engineering](#feature-engineering)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Top-K Recommendations](#top-k-recommendations)
- [Running Tests](#running-tests)
- [Development](#development)

---

## Overview

The matching engine takes a pool of mentors and a pool of mentees and exposes two main entry points:

| Method | Purpose |
|---|---|
| `match()` | Globally optimized 1-to-1 assignments — respects mentor capacity and maximises total compatibility |
| `recommend(top_k)` | Top-k ranked mentor suggestions per mentee — no capacity enforcement, ideal for surfacing options to the user before a final assignment |

Each result is a `Match` object containing:

- An overall compatibility **score** (0–1)
- Individual component scores (skills, expertise, experience, industry, availability, etc.)
- Human-readable **reasons** explaining why the pair was selected
- Any **constraint violations** if a pair is invalid

---

## Architecture

The engine exposes two pipelines through `MatchingService`:

**`match()` — globally optimized assignment**
```
Mentors + Mentees
       ↓
Candidate Generation      ← eligibility checks, per-pair scoring
       ↓
Match Scoring             ← weighted feature engineering algorithms
       ↓
Global Optimization       ← linear assignment, capacity constraints
       ↓
list[Match]               ← one match per mentee
```

**`recommend(top_k)` — ranked suggestions**
```
Mentors + Mentees
       ↓
Candidate Generation      ← eligibility checks, per-pair scoring
       ↓
Top-k selection           ← no capacity enforcement
       ↓
dict[mentee_id, list[Match]]   ← up to k matches per mentee
```

| Stage | Class | Responsibility |
|---|---|---|
| Candidate Generation | `CandidateGenerator` | Filters ineligible pairs, scores remaining candidates |
| Constraint Validation | `ConstraintValidator` | Enforces hard rules (capacity, availability minimums, etc.) |
| Scoring | `MatchScorer` | Computes weighted compatibility using `feature_engineering` algorithms |
| Optimization | `MatchingOptimizer` | Solves the assignment problem to maximise global compatibility |
| Orchestration | `MatchingService` | Ties all stages together into a single `match()` call |

---

## Project Structure

```
mentor-matching-engine/
├── pyproject.toml
├── README.md
└── src/
    └── matching_engine/
        ├── constraints/
        │   └── validator.py                # Hard constraint checks
        ├── feature_engineering/            # Core scoring algorithms
        │   ├── constants.py                # Industry groups, TZ offsets, thresholds
        │   ├── feature_builder.py          # Experience gap, industry, availability scores
        │   ├── goal_encoder.py             # TF-cosine goal alignment
        │   └── skill_encoder.py            # Jaccard + coverage skill scoring
        ├── features/
        │   ├── goal_features.py            # Goal feature extractor (used in tests)
        │   ├── preference_features.py      # Mentee preference matching (active)
        │   └── skill_features.py           # Skill feature extractor (used in tests)
        ├── models/
        │   ├── match.py                    # Match result model
        │   ├── mentee.py                   # Mentee data model
        │   └── mentor.py                   # Mentor data model
        ├── optimization/
        │   ├── candidate_generator.py      # Pre-filter and score candidates
        │   └── optimizer.py               # Global assignment optimization
        ├── scoring/
        │   └── scorer.py                   # Weighted multi-feature scorer
        └── service/
            └── matching_service.py         # High-level entry point
```

---

## Models

### `Mentor`

| Field | Type | Description |
|---|---|---|
| `id` | `str` | Unique identifier |
| `name` | `str` | Display name |
| `skills` | `list[str]` | Skills the mentor possesses |
| `expertise` | `list[str]` | Specialist areas |
| `industry` | `str \| None` | Current or primary industry |
| `years_experience` | `int` | Total years of professional experience |
| `experience_level` | `str \| None` | e.g. `"senior"`, `"principal"` |
| `mentoring_topics` | `list[str]` | Topics the mentor is willing to cover |
| `availability` | `list[str]` | Available time slots |
| `timezone` | `str \| None` | Timezone abbreviation (e.g. `"EST"`, `"PST"`) |
| `preferred_mentee_experience_levels` | `list[str]` | Mentee levels the mentor prefers |
| `preferred_industries` | `list[str]` | Industries the mentor prefers |
| `max_mentees` | `int` | Maximum number of mentees (default `1`) |
| `current_mentees` | `int` | Current active mentees |
| `available_capacity` | `int` *(property)* | `max_mentees - current_mentees` |

### `Mentee`

| Field | Type | Description |
|---|---|---|
| `id` | `str` | Unique identifier |
| `name` | `str` | Display name |
| `skills` | `list[str]` | Skills the mentee already has |
| `experience_level` | `str \| None` | e.g. `"junior"`, `"mid"` |
| `years_experience` | `int` | Total years of professional experience |
| `industry` | `str \| None` | Current or target industry |
| `goals` | `list[str]` | High-level career or learning goals |
| `skills_to_learn` | `list[str]` | Specific skills the mentee wants to develop |
| `interests` | `list[str]` | General interests (fallback when `skills_to_learn` is empty) |
| `availability` | `list[str]` | Available time slots |
| `timezone` | `str \| None` | Timezone abbreviation (e.g. `"EST"`, `"PST"`) |
| `preferred_industries` | `list[str]` | Industries the mentee wants exposure to |
| `preferred_mentor_experience_levels` | `list[str]` | Mentor seniority preferences |
| `preferred_mentor_topics` | `list[str]` | Topics the mentee wants covered |

### `Match`

| Field | Type | Description |
|---|---|---|
| `mentor_id` | `str` | Matched mentor |
| `mentee_id` | `str` | Matched mentee |
| `score` | `float` | Overall compatibility (0–1) |
| `skill_score` | `float` | Skill alignment component |
| `goal_score` | `float` | Goal alignment component |
| `expertise_score` | `float` | Mentor expertise coverage component |
| `experience_score` | `float` | Experience compatibility component |
| `industry_score` | `float` | Industry alignment component |
| `availability_score` | `float` | Availability overlap component |
| `preference_score` | `float` | Preference satisfaction component |
| `is_valid` | `bool` | Whether all constraints are satisfied |
| `reasons` | `list[str]` | Human-readable match explanations |
| `constraint_violations` | `list[str]` | Any hard constraint failures |

---

## Scoring Dimensions

`MatchScorer` computes a weighted final score using algorithms from the `feature_engineering` module:

| Dimension | Weight | Algorithm | What is measured |
|---|---|---|---|
| **Skill** | 40% | `combined_skill_score` | `0.6 × coverage + 0.4 × Jaccard` — with partial-name boosting (e.g. `"python"` matches `"python 3"`) |
| **Expertise** | 20% | *(scorer)* | Fraction of the mentee's `skills_to_learn` covered by the mentor's skills + expertise + topics |
| **Industry** | 15% | `industry_match_score` | Exact match → 1.0 · same industry cluster → 0.5 · preferred_industries → 1.0 · no match → 0.0 |
| **Experience** | 10% | `experience_gap_score` | Level-rank when both levels set; continuous gap-curve (`years_experience`) otherwise |
| **Availability** | 10% | `availability_score` | Slot overlap (60%) + timezone diff (40%) — TZ only factored in when both sides provide one |
| **Topic** | 5% | `PreferenceFeatureExtractor` | Fraction of the mentee's preferred topics the mentor covers |

**Goal score** (TF-cosine semantic similarity via `goal_alignment_score`) is computed and returned for explainability but does not contribute to the weighted score yet.

---

## Feature Engineering

The `feature_engineering` package provides the low-level scoring primitives used by `MatchScorer`.

### `skill_encoder.py`

| Function | Description |
|---|---|
| `combined_skill_score(mentor, mentee)` | Primary skill score — `0.6 × coverage + 0.4 × Jaccard` |
| `skill_coverage_score(mentor, mentee)` | Mentee-perspective: fraction of desired skills the mentor covers |
| `jaccard_skill_score(mentor, mentee)` | Symmetric Jaccard similarity with partial-match boosting |

### `goal_encoder.py`

| Function | Description |
|---|---|
| `goal_alignment_score(mentor_text, mentee_text)` | TF-cosine similarity between mentor's goal text and mentee's goal text |

### `feature_builder.py`

| Function | Description |
|---|---|
| `experience_gap_score(mentor, mentee)` | Continuous score based on years-of-experience gap (peaks at `OPTIMAL_EXPERIENCE_GAP_YEARS`) |
| `industry_match_score(mentor, mentee)` | 1.0 exact · 0.5 same cluster · 0.0 different |
| `availability_score(mentor, mentee)` | `0.6 × slot_overlap + 0.4 × timezone_score` |
| `slot_overlap_score(mentor_slots, mentee_slots)` | Fraction of mentee's slots the mentor covers |
| `timezone_score(mentor_tz, mentee_tz)` | 1.0 same · 0.75 ≤3 h diff · 0.5 ≤6 h diff · 0.0 incompatible |

### `constants.py`

Configurable thresholds and lookup tables:

| Constant | Default | Description |
|---|---|---|
| `MIN_EXPERIENCE_GAP_YEARS` | `2` | Minimum gap for a non-zero experience score |
| `OPTIMAL_EXPERIENCE_GAP_YEARS` | `7` | Gap that yields a perfect experience score |
| `MAX_COMPATIBLE_TZ_DIFF_HOURS` | `6` | Max timezone difference before score drops to 0 |
| `INDUSTRY_GROUPS` | 11 clusters | Maps industry names to broad groups (technology, finance, healthcare, …) |
| `TIMEZONE_UTC_OFFSETS` | 50+ entries | Maps TZ abbreviations (e.g. `"PST"`, `"IST"`) to UTC offset hours |

---

## Installation

Requires **Python ≥ 3.11** and [`uv`](https://github.com/astral-sh/uv).

```bash
# Clone the repo and move into the package directory
cd mentor-matching-engine

# Install all dependencies (including dev)
uv sync
```

---

## Quick Start

```python
from matching_engine.models.mentor import Mentor
from matching_engine.models.mentee import Mentee
from matching_engine.service.matching_service import MatchingService

mentors = [
    Mentor(
        id="m1",
        name="Alice Chen",
        skills=["python", "machine-learning", "system-design"],
        expertise=["data-engineering", "mlops"],
        industry="technology",
        years_experience=10,
        experience_level="senior",
        mentoring_topics=["career-growth", "technical-interviews"],
        availability=["weekday-evenings", "saturday-morning"],
        timezone="PST",
        max_mentees=2,
    )
]

mentees = [
    Mentee(
        id="e1",
        name="Bob Kim",
        skills=["python"],
        experience_level="junior",
        years_experience=1,
        industry="technology",
        goals=["become-ml-engineer"],
        skills_to_learn=["machine-learning", "mlops"],
        availability=["weekday-evenings"],
        timezone="PST",
        preferred_mentor_experience_levels=["senior", "principal"],
    )
]

service = MatchingService()
matches = service.match(mentors, mentees)

for match in matches:
    print(f"{match.mentor_id} → {match.mentee_id}  score={match.score:.3f}")
    for reason in match.reasons:
        print(f"  • {reason}")
```

---

## Top-K Recommendations

`recommend()` scores every eligible mentor for each mentee and returns the top-k ranked options **without** running global optimization or enforcing capacity constraints. This is useful for:

- Showing candidates to a mentee before committing to an assignment
- Powering a search/browse UI
- Debugging — understanding why a particular mentor ranks where it does

```python
service = MatchingService()

recommendations = service.recommend(
    mentors,
    mentees,
    top_k=3,          # default is 3
)

# recommendations: dict[mentee_id, list[Match]]
for mentee_id, matches in recommendations.items():
    print(f"\nTop recommendations for {mentee_id}:")
    for rank, match in enumerate(matches, start=1):
        print(f"  #{rank}  mentor={match.mentor_id}  score={match.score:.3f}")
        for reason in match.reasons:
            print(f"       • {reason}")
```

**Key differences from `match()`:**

| | `match()` | `recommend(top_k)` |
|---|---|---|
| Return type | `list[Match]` | `dict[str, list[Match]]` |
| Optimization | Global (maximises total score) | None (per-mentee ranking only) |
| Capacity enforced | ✅ Yes | ❌ No |
| Use case | Final assignment | Exploration / UI suggestions |
| Results per mentee | Exactly 1 | Up to `top_k` |

---

## Running Tests

```bash
uv run pytest
```

All tests live under `tests/` and cover each major component:

| Test file | Component |
|---|---|
| `test_candidate_generator.py` | `CandidateGenerator` |
| `test_goal_features.py` | `GoalFeatureExtractor` |
| `test_matching_service.py` | `MatchingService` (end-to-end) |
| `test_optimizer.py` | `MatchingOptimizer` |
| `test_preference_features.py` | `PreferenceFeatureExtractor` |
| `test_recommend.py` | `MatchingService.recommend()` |
| `test_scorer.py` | `MatchScorer` |
| `test_skill_features.py` | `SkillFeatureExtractor` |
| `test_validator.py` | `ConstraintValidator` |

---

## Development

The project uses [`uv`](https://github.com/astral-sh/uv) for dependency management and [`hatchling`](https://hatch.pypa.io) as the build backend.

```bash
# Add a runtime dependency
uv add <package>

# Add a dev-only dependency
uv add --dev <package>

# Build the wheel
uv build
```

Dependencies are pinned in `uv.lock` for reproducible installs.
