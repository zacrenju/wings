"""
Goal alignment encoder — computes semantic similarity between
mentor teaching goals and mentee learning goals using TF-IDF + cosine similarity.
"""
from __future__ import annotations

import math
import re
from collections import Counter


def _tokenise(text: str) -> list[str]:
    """Lowercase, strip punctuation, tokenise."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return [t for t in text.split() if len(t) > 2]


_STOP_WORDS = {
    "the", "and", "for", "are", "but", "not", "with", "this", "that",
    "have", "from", "they", "will", "your", "you", "can", "want",
    "help", "learn", "teach", "work", "also", "more", "some", "how",
}


def _remove_stopwords(tokens: list[str]) -> list[str]:
    return [t for t in tokens if t not in _STOP_WORDS]


def _tf(tokens: list[str]) -> dict[str, float]:
    if not tokens:
        return {}
    counts = Counter(tokens)
    total = len(tokens)
    return {word: count / total for word, count in counts.items()}


def _cosine_similarity(vec_a: dict[str, float], vec_b: dict[str, float]) -> float:
    """Cosine similarity between two sparse TF vectors."""
    shared_keys = set(vec_a.keys()) & set(vec_b.keys())
    dot = sum(vec_a[k] * vec_b[k] for k in shared_keys)
    mag_a = math.sqrt(sum(v ** 2 for v in vec_a.values()))
    mag_b = math.sqrt(sum(v ** 2 for v in vec_b.values()))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def goal_alignment_score(mentor_goals: str, mentee_goals: str) -> float:
    """
    Compute goal alignment score in [0.0, 1.0].

    Uses TF-based cosine similarity (no corpus needed for IDF; works
    well with small texts like profile goal statements).
    """
    mentor_tokens = _remove_stopwords(_tokenise(mentor_goals))
    mentee_tokens = _remove_stopwords(_tokenise(mentee_goals))

    if not mentor_tokens or not mentee_tokens:
        return 0.0

    tf_mentor = _tf(mentor_tokens)
    tf_mentee = _tf(mentee_tokens)

    return round(_cosine_similarity(tf_mentor, tf_mentee), 6)

