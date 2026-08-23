# Wings Backend — Mentor Matching API

A FastAPI service that exposes the [mentor-matching-engine](../mentor-matching-engine/README.md) over HTTP. It provides two endpoints: a globally-optimized assignment endpoint and a top-k ranked recommendations endpoint.

---

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Endpoints](#endpoints)
- [Request & Response Schemas](#request--response-schemas)
- [Installation](#installation)
- [Running the Server](#running-the-server)
- [Interactive Docs](#interactive-docs)
- [Example Requests](#example-requests)
- [Running Tests](#running-tests)
- [Configuration](#configuration)
- [Development](#development)

---

## Overview

| Endpoint | Method | Description |
|---|---|---|
| `/health` | `GET` | Health check |
| `/api/v1/match` | `POST` | Globally optimized 1-to-1 mentor-mentee assignments |
| `/api/v1/recommend` | `POST` | Top-k ranked mentor suggestions per mentee |

The backend is a thin HTTP wrapper — all matching logic lives in the `mentor-matching-engine` package, which is installed as a local editable dependency.

---

## Project Structure

```
backend/
├── main.py                         # FastAPI app entry point
├── pyproject.toml
├── test_api.py                     # Smoke-test script (requires running server)
└── src/
    └── mentor_match/
        ├── api/
        │   └── matching.py         # /api/v1/match and /api/v1/recommend routes
        ├── models/
        │   └── schemas.py          # Request / response Pydantic schemas
        └── services/
            └── matching.py         # Singleton MatchingService (FastAPI Depends)
```

---

## Endpoints

### `GET /health`

Simple liveness probe.

**Response**
```json
{ "status": "ok" }
```

---

### `POST /api/v1/match`

Runs the full matching pipeline:

1. Candidate generation with eligibility checks
2. Multi-dimensional compatibility scoring
3. Global linear-assignment optimization (respects mentor capacity)

Returns one `Match` per mentee that could be assigned a mentor.

---

### `POST /api/v1/recommend`

Scores every eligible mentor for each mentee independently and returns the top-k highest-scoring options **without** enforcing capacity constraints. The same mentor may appear in recommendations for multiple mentees.

---

## Request & Response Schemas

### Mentor fields

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | `string` | ✅ | Unique identifier |
| `name` | `string` | ✅ | Display name |
| `skills` | `string[]` | | Skills the mentor possesses |
| `expertise` | `string[]` | | Specialist areas |
| `industry` | `string` | | Primary industry |
| `years_experience` | `integer` | | Total years of experience |
| `experience_level` | `string` | | `"junior"` · `"mid"` · `"senior"` · `"lead"` · `"principal"` · `"executive"` |
| `mentoring_topics` | `string[]` | | Topics the mentor covers |
| `availability` | `string[]` | | Available time slots |
| `timezone` | `string` | | TZ abbreviation e.g. `"PST"`, `"EST"`, `"IST"` |
| `preferred_mentee_experience_levels` | `string[]` | | Mentee levels the mentor accepts |
| `preferred_industries` | `string[]` | | Industries the mentor prefers |
| `max_mentees` | `integer` | | Capacity (default `1`) |
| `current_mentees` | `integer` | | Current active mentees (default `0`) |

### Mentee fields

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | `string` | ✅ | Unique identifier |
| `name` | `string` | ✅ | Display name |
| `skills` | `string[]` | | Skills already held |
| `skills_to_learn` | `string[]` | | Skills the mentee wants to develop |
| `goals` | `string[]` | | High-level career or learning goals |
| `interests` | `string[]` | | General interests (fallback for skill matching) |
| `industry` | `string` | | Current or target industry |
| `years_experience` | `integer` | | Total years of experience |
| `experience_level` | `string` | | e.g. `"junior"`, `"mid"` |
| `availability` | `string[]` | | Available time slots |
| `timezone` | `string` | | TZ abbreviation |
| `preferred_industries` | `string[]` | | Preferred mentor industries |
| `preferred_mentor_experience_levels` | `string[]` | | Preferred mentor seniority levels |
| `preferred_mentor_topics` | `string[]` | | Topics the mentee wants covered |

### Match response fields

| Field | Type | Description |
|---|---|---|
| `mentor_id` | `string` | Matched mentor |
| `mentee_id` | `string` | Matched mentee |
| `score` | `float` | Overall compatibility score (0–1) |
| `skill_score` | `float` | Skill alignment component |
| `goal_score` | `float` | Goal alignment component (TF-cosine) |
| `expertise_score` | `float` | Mentor expertise coverage |
| `experience_score` | `float` | Experience compatibility |
| `industry_score` | `float` | Industry alignment |
| `availability_score` | `float` | Availability overlap |
| `preference_score` | `float` | Mentee preference satisfaction |
| `is_valid` | `bool` | Whether all hard constraints are met |
| `reasons` | `string[]` | Human-readable match explanations |
| `constraint_violations` | `string[]` | Any hard constraint failures |

---

## Installation

Requires **Python ≥ 3.11** and [`uv`](https://github.com/astral-sh/uv).

```bash
cd backend
uv sync
```

This installs all dependencies including the local `mentor-matching-engine` package (referenced via a `uv.sources` path dependency — no separate install step needed).

---

## Running the Server

```bash
# Development — auto-reload on file changes
uv run uvicorn main:app --reload --port 8000

# Production
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## Interactive Docs

Once the server is running, open your browser at:

| UI | URL |
|---|---|
| Swagger UI | [http://localhost:8000/docs](http://localhost:8000/docs) |
| ReDoc | [http://localhost:8000/redoc](http://localhost:8000/redoc) |
| OpenAPI JSON | [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json) |

---

## Example Requests

### `POST /api/v1/match`

```json
{
  "mentors": [
    {
      "id": "m1",
      "name": "Alice Chen",
      "skills": ["python", "machine-learning"],
      "expertise": ["mlops", "data-engineering"],
      "industry": "technology",
      "years_experience": 10,
      "experience_level": "senior",
      "mentoring_topics": ["career-growth", "technical-interviews"],
      "availability": ["weekday-evenings", "saturday-morning"],
      "timezone": "PST",
      "max_mentees": 2
    }
  ],
  "mentees": [
    {
      "id": "e1",
      "name": "Bob Kim",
      "skills": ["python"],
      "skills_to_learn": ["machine-learning", "mlops"],
      "industry": "technology",
      "years_experience": 1,
      "experience_level": "junior",
      "availability": ["weekday-evenings"],
      "timezone": "PST",
      "preferred_mentor_experience_levels": ["senior", "principal"]
    }
  ]
}
```

**Response**

```json
{
  "matches": [
    {
      "mentor_id": "m1",
      "mentee_id": "e1",
      "score": 0.87,
      "skill_score": 0.8,
      "goal_score": 0.7071,
      "expertise_score": 1.0,
      "experience_score": 1.0,
      "industry_score": 1.0,
      "availability_score": 1.0,
      "preference_score": 0.0,
      "is_valid": true,
      "reasons": [
        "Partial skill alignment.",
        "Mentor expertise aligns with the mentee's learning needs.",
        "Industry preference is aligned.",
        "Experience levels are compatible.",
        "Availability is fully aligned."
      ],
      "constraint_violations": []
    }
  ],
  "total": 1
}
```

---

### `POST /api/v1/recommend`

```json
{
  "mentors": [ ... ],
  "mentees": [
    {
      "id": "e1",
      "name": "Bob Kim",
      "skills_to_learn": ["machine-learning", "mlops"],
      "industry": "technology",
      "experience_level": "junior"
    }
  ],
  "top_k": 3
}
```

**Response**

```json
{
  "recommendations": {
    "e1": [
      { "mentor_id": "m1", "score": 0.87, "reasons": ["..."], "..." : "..." },
      { "mentor_id": "m3", "score": 0.42, "reasons": ["..."], "..." : "..." },
      { "mentor_id": "m2", "score": 0.13, "reasons": ["..."], "..." : "..." }
    ]
  },
  "top_k": 3,
  "mentee_count": 1
}
```

---

## Running Tests

A smoke-test script is included that hits a live server:

```bash
# Start the server first
uv run uvicorn main:app --port 8000 &

# Run the smoke test
uv run python test_api.py
```

For proper automated tests using `pytest` and `httpx`:

```bash
uv run pytest
```

---

## Configuration

The app currently uses no external configuration. To add environment-specific settings (e.g. CORS origins, log level), create a `.env` file and load it via `python-dotenv`:

```env
CORS_ORIGINS=https://your-frontend.example.com
LOG_LEVEL=info
```

Then update `main.py` to read from `os.environ`.

---

## Development

```bash
# Install dependencies (including dev extras)
uv sync

# Add a runtime dependency
uv add <package>

# Add a dev-only dependency
uv add --dev <package>
```

The `mentor-matching-engine` is installed as an **editable path dependency** — any changes you make to the engine are immediately reflected in the backend without reinstalling.

