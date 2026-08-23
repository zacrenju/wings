"""
FastAPI router for mentor-matching endpoints.

Routes
------
POST /api/v1/match
    Globally optimized mentor-mentee assignments.
    Respects mentor capacity and maximises total compatibility.

POST /api/v1/recommend
    Top-k ranked mentor suggestions per mentee.
    No capacity enforcement — useful for surfacing options in a UI.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from matching_engine.service.matching_service import MatchingService

from mentor_match.models.schemas import (
    MatchListResponse,
    MatchRequest,
    RecommendRequest,
    RecommendResponse,
)
from mentor_match.services.matching import get_matching_service

router = APIRouter(prefix="/api/v1", tags=["matching"])


# ---------------------------------------------------------------------------
# POST /api/v1/match
# ---------------------------------------------------------------------------

@router.post(
    "/match",
    response_model=MatchListResponse,
    summary="Globally optimized mentor-mentee matching",
    description=(
        "Runs the full matching pipeline: candidate generation → scoring → "
        "global linear assignment optimization. "
        "Each mentee receives at most one mentor; mentor capacity is enforced."
    ),
    status_code=status.HTTP_200_OK,
)
def match(
    body: MatchRequest,
    service: MatchingService = Depends(get_matching_service),
) -> MatchListResponse:
    try:
        matches = service.match(
            mentors=body.mentors,
            mentees=body.mentees,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Matching failed: {exc}",
        ) from exc

    return MatchListResponse.from_matches(matches)


# ---------------------------------------------------------------------------
# POST /api/v1/recommend
# ---------------------------------------------------------------------------

@router.post(
    "/recommend",
    response_model=RecommendResponse,
    summary="Top-k mentor recommendations per mentee",
    description=(
        "Scores every eligible mentor for each mentee and returns the "
        "top-k highest-scoring options per mentee. "
        "No global optimization or capacity enforcement is applied — "
        "the same mentor may appear for multiple mentees."
    ),
    status_code=status.HTTP_200_OK,
)
def recommend(
    body: RecommendRequest,
    service: MatchingService = Depends(get_matching_service),
) -> RecommendResponse:
    try:
        recommendations = service.recommend(
            mentors=body.mentors,
            mentees=body.mentees,
            top_k=body.top_k,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recommendation failed: {exc}",
        ) from exc

    return RecommendResponse.from_recommendations(
        recommendations=recommendations,
        top_k=body.top_k,
    )

