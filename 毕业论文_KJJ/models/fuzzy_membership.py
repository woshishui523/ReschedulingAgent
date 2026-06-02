"""Fuzzy membership model utilities.

Defines a simple fuzzy set representation used by the decision engine.
"""
from dataclasses import dataclass
from typing import Callable, Dict


@dataclass
class FuzzyMembership:
    name: str
    membership_fn: Callable[[float], float]

    def membership(self, x: float) -> float:
        return float(self.membership_fn(x))


def triangular(a: float, b: float, c: float):
    def fn(x: float) -> float:
        if x <= a or x >= c:
            return 0.0
        if a < x < b:
            return (x - a) / (b - a)
        return (c - x) / (c - b)

    return fn


__all__ = ["FuzzyMembership", "triangular"]
