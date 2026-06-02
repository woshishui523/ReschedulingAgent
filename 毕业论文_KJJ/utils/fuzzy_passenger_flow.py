"""Utilities for computing fuzzy passenger flow estimations."""
from typing import List, Dict


def compute_passenger_flow(counts: List[int]) -> Dict[str, float]:
    """Compute a few aggregate statistics from raw passenger counts.

    Returns a dict with total, mean and a simple congestion score.
    """
    if not counts:
        return {"total": 0.0, "mean": 0.0, "congestion": 0.0}
    total = sum(counts)
    mean = total / len(counts)
    congestion = min(1.0, mean / 100.0)
    return {"total": float(total), "mean": float(mean), "congestion": float(congestion)}


__all__ = ["compute_passenger_flow"]
