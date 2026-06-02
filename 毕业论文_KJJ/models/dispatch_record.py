"""Dispatch record data model (dataclass-based).

Lightweight representation used by the decision engine and tests.
"""
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional


@dataclass
class DispatchRecord:
    id: Optional[int]
    created_at: str
    plan: Dict[str, Any]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


__all__ = ["DispatchRecord"]
