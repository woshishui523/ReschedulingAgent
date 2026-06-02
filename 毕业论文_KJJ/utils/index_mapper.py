"""Index mapping and simple neighborhood query helpers."""
from typing import List, Tuple


def nearest_indices(center: int, radius: int, max_index: int) -> List[int]:
    start = max(0, center - radius)
    end = min(max_index, center + radius)
    return list(range(start, end + 1))


__all__ = ["nearest_indices"]
