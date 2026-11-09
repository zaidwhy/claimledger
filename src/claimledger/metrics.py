import math


def recall_any(ranked_session_ids: list[str], evidence: list[str], k: int) -> bool:
    """True when at least one evidence session is in the top k."""
    top = set(ranked_session_ids[:k])
    return any(session_id in top for session_id in evidence)


def recall_all(ranked_session_ids: list[str], evidence: list[str], k: int) -> bool:
    top = set(ranked_session_ids[:k])
    return all(session_id in top for session_id in evidence)


def wilson_interval(hits: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95 percent Wilson score interval for a proportion."""
    if n <= 0:
        raise ValueError("n must be positive")
    p = hits / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)
