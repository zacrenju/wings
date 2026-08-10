import pytest
from matching_engine.optimization.optimizer import (
    MatchingOptimizer,
)
from matching_engine.optimization.candidate_generator import (
    MatchCandidate,
)


def candidate(
    mentor_id: str,
    mentee_id: str,
    score: float,
    features: dict[str, float] | None = None,
) -> MatchCandidate:
    """
    Helper for creating MatchCandidate objects.
    """

    return MatchCandidate(
        mentor_id=mentor_id,
        mentee_id=mentee_id,
        score=score,
        features=features or {
            "skill_score": score,
        },
    )


def test_single_mentee_single_mentor():
    """
    One mentee and one mentor should produce
    one assignment.
    """

    candidates = [
        candidate(
            mentor_id="m1",
            mentee_id="e1",
            score=0.90,
        )
    ]

    optimizer = MatchingOptimizer()

    result = optimizer.optimize(
        candidates,
        mentor_capacities={
            "m1": 1,
        },
    )

    assert len(result) == 1

    assert result[0].mentor_id == "m1"
    assert result[0].mentee_id == "e1"
    assert result[0].score == 0.90


def test_best_mentor_is_selected():
    """
    When a mentee has multiple possible mentors,
    the highest scoring mentor should be selected.
    """

    candidates = [
        candidate("m1", "e1", 0.70),
        candidate("m2", "e1", 0.90),
        candidate("m3", "e1", 0.80),
    ]

    optimizer = MatchingOptimizer()

    result = optimizer.optimize(
        candidates,
        mentor_capacities={
            "m1": 1,
            "m2": 1,
            "m3": 1,
        },
    )

    assert len(result) == 1
    assert result[0].mentor_id == "m2"
    assert result[0].score == 0.90


def test_each_mentee_gets_at_most_one_mentor():
    """
    A mentee must never receive multiple mentors.
    """

    candidates = [
        candidate("m1", "e1", 0.90),
        candidate("m2", "e1", 0.80),
        candidate("m3", "e1", 0.70),
    ]

    optimizer = MatchingOptimizer()

    result = optimizer.optimize(
        candidates,
        mentor_capacities={
            "m1": 1,
            "m2": 1,
            "m3": 1,
        },
    )

    assert len(result) == 1
    assert result[0].mentee_id == "e1"


def test_mentor_capacity_is_respected():
    """
    A mentor with capacity two can mentor two mentees.
    """

    candidates = [
        candidate("m1", "e1", 0.90),
        candidate("m1", "e2", 0.85),
        candidate("m1", "e3", 0.80),
    ]

    optimizer = MatchingOptimizer()

    result = optimizer.optimize(
        candidates,
        mentor_capacities={
            "m1": 2,
        },
    )

    assert len(result) == 2

    assert {
        assignment.mentee_id
        for assignment in result
    } == {
        "e1",
        "e2",
    }


def test_multiple_mentors_and_multiple_mentees():
    """
    Multiple mentors and mentees should be matched
    according to the best global allocation.
    """

    candidates = [
        candidate("m1", "e1", 0.90),
        candidate("m2", "e1", 0.70),
        candidate("m1", "e2", 0.80),
        candidate("m2", "e2", 0.95),
    ]

    optimizer = MatchingOptimizer()

    result = optimizer.optimize(
        candidates,
        mentor_capacities={
            "m1": 1,
            "m2": 1,
        },
    )

    assert len(result) == 2

    assignments = {
        assignment.mentee_id: assignment.mentor_id
        for assignment in result
    }

    assert assignments["e1"] == "m1"
    assert assignments["e2"] == "m2"


def test_global_optimization_beats_greedy():
    """
    This is the most important optimizer test.

    Scores:

                 M1       M2
        E1      0.95     0.90
        E2      0.94     0.10

    Greedy approach:
        E1 -> M1 = 0.95
        E2 -> M2 = 0.10

        Total = 1.05

    Optimal approach:
        E1 -> M2 = 0.90
        E2 -> M1 = 0.94

        Total = 1.84

    The optimizer should find the global solution.
    """

    candidates = [
        candidate("m1", "e1", 0.95),
        candidate("m2", "e1", 0.90),
        candidate("m1", "e2", 0.94),
        candidate("m2", "e2", 0.10),
    ]

    optimizer = MatchingOptimizer()

    result = optimizer.optimize(
        candidates,
        mentor_capacities={
            "m1": 1,
            "m2": 1,
        },
    )

    assert len(result) == 2

    assignments = {
        assignment.mentee_id: assignment.mentor_id
        for assignment in result
    }

    assert assignments["e1"] == "m2"
    assert assignments["e2"] == "m1"

    total_score = sum(
        assignment.score
        for assignment in result
    )

    assert round(total_score, 2) == 1.84


def test_unavailable_mentor_capacity_is_not_used():
    """
    A mentor with zero capacity must not receive
    any mentees.
    """

    candidates = [
        candidate("m1", "e1", 0.99),
        candidate("m2", "e1", 0.80),
    ]

    optimizer = MatchingOptimizer()

    result = optimizer.optimize(
        candidates,
        mentor_capacities={
            "m1": 0,
            "m2": 1,
        },
    )

    assert len(result) == 1

    assert result[0].mentor_id == "m2"


def test_no_candidates_returns_empty_result():
    """
    Empty candidate input should produce no matches.
    """

    optimizer = MatchingOptimizer()

    result = optimizer.optimize(
        [],
        mentor_capacities={
            "m1": 1,
            "m2": 1,
        },
    )

    assert result == []


def test_no_capacity_returns_empty_result():
    """
    If all mentors have zero capacity, no assignments
    should be produced.
    """

    candidates = [
        candidate("m1", "e1", 0.95),
        candidate("m2", "e1", 0.90),
    ]

    optimizer = MatchingOptimizer()

    result = optimizer.optimize(
        candidates,
        mentor_capacities={
            "m1": 0,
            "m2": 0,
        },
    )

    assert result == []


def test_missing_candidate_is_not_created_as_match():
    """
    An absent mentor-mentee pair must never become a
    fake zero-score match.
    """

    candidates = [
        candidate("m1", "e1", 0.90),
        candidate("m2", "e2", 0.80),
    ]

    optimizer = MatchingOptimizer()

    result = optimizer.optimize(
        candidates,
        mentor_capacities={
            "m1": 1,
            "m2": 1,
        },
    )

    assert len(result) == 2

    pairs = {
        (
            assignment.mentor_id,
            assignment.mentee_id,
        )
        for assignment in result
    }

    assert ("m1", "e1") in pairs
    assert ("m2", "e2") in pairs

    assert ("m1", "e2") not in pairs
    assert ("m2", "e1") not in pairs


def test_duplicate_candidate_keeps_highest_score():
    """
    If duplicate candidates exist for the same mentor/mentee
    pair, the optimizer should use the highest score.
    """

    candidates = [
        candidate("m1", "e1", 0.70),
        candidate("m1", "e1", 0.90),
    ]

    optimizer = MatchingOptimizer()

    result = optimizer.optimize(
        candidates,
        mentor_capacities={
            "m1": 1,
        },
    )

    assert len(result) == 1
    assert result[0].score == 0.90


def test_features_are_preserved():
    """
    Candidate feature information should be carried into
    the final assignment.
    """

    features = {
        "skill_score": 1.0,
        "expertise_score": 0.8,
        "industry_score": 1.0,
        "availability_score": 0.5,
    }

    candidates = [
        candidate(
            "m1",
            "e1",
            0.85,
            features,
        )
    ]

    optimizer = MatchingOptimizer()

    result = optimizer.optimize(
        candidates,
        mentor_capacities={
            "m1": 1,
        },
    )

    assert len(result) == 1

    assert result[0].features == features


def test_results_are_sorted_by_score():
    """
    Final assignments should be returned from highest
    score to lowest score.
    """

    candidates = [
        candidate("m1", "e1", 0.70),
        candidate("m2", "e2", 0.95),
        candidate("m3", "e3", 0.80),
    ]

    optimizer = MatchingOptimizer()

    result = optimizer.optimize(
        candidates,
        mentor_capacities={
            "m1": 1,
            "m2": 1,
            "m3": 1,
        },
    )

    assert len(result) == 3

    scores = [
        assignment.score
        for assignment in result
    ]

    assert scores == [
        0.95,
        0.80,
        0.70,
    ]


def test_grouped_candidates_are_supported():
    """
    optimize_from_grouped_candidates() should accept
    the dictionary returned by CandidateGenerator.generate().
    """

    grouped_candidates = {
        "e1": [
            candidate("m1", "e1", 0.90),
            candidate("m2", "e1", 0.70),
        ],
        "e2": [
            candidate("m1", "e2", 0.80),
            candidate("m2", "e2", 0.95),
        ],
    }

    optimizer = MatchingOptimizer()

    result = optimizer.optimize_from_grouped_candidates(
        grouped_candidates,
        mentor_capacities={
            "m1": 1,
            "m2": 1,
        },
    )

    assert len(result) == 2

    assignments = {
        assignment.mentee_id: assignment.mentor_id
        for assignment in result
    }

    assert assignments["e1"] == "m1"
    assert assignments["e2"] == "m2"
