"""Feedback model dataclass.

Represents user/operator/system feedback stored in the database.
"""
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional


@dataclass
class Feedback:
    id: Optional[int]
    timestamp: str
    source: str
    payload: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


__all__ = ["Feedback"]
