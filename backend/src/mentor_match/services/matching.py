"""
Thin adapter that wraps the matching_engine.MatchingService
for use inside the FastAPI application.

A single shared instance is created at startup and reused
across requests (MatchingService is stateless).
"""
from __future__ import annotations

from functools import lru_cache

from matching_engine.service.matching_service import MatchingService


@lru_cache(maxsize=1)
def get_matching_service() -> MatchingService:
    """
    Return the shared MatchingService instance.

    Using lru_cache(maxsize=1) means the service is instantiated
    once on first call and reused for the lifetime of the process —
    equivalent to a singleton without requiring a global variable.

    Inject via FastAPI's Depends():

        from mentor_match.services.matching import get_matching_service

        @router.post("/match")
        def match(
            body: MatchRequest,
            service: MatchingService = Depends(get_matching_service),
        ): ...
    """
    return MatchingService()

