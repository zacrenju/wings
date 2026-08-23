"""
Wings backend — FastAPI application entry point.

Start the server:
    uv run uvicorn main:app --reload --port 8000

Interactive docs:
    http://localhost:8000/docs
    http://localhost:8000/redoc
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from mentor_match.api.matching import router as matching_router

app = FastAPI(
    title="Wings — Mentor Matching API",
    description=(
        "REST API for the Wings mentor-matching engine.\n\n"
        "## Endpoints\n\n"
        "| Method | Path | Description |\n"
        "|---|---|---|\n"
        "| POST | `/api/v1/match` | Globally optimized 1-to-1 assignments |\n"
        "| POST | `/api/v1/recommend` | Top-k ranked suggestions per mentee |"
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# CORS — allow all origins in development; tighten in production
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(matching_router)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health", tags=["ops"], summary="Health check")
def health() -> dict[str, str]:
    return {"status": "ok"}
