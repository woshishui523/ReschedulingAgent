"""Decision engine service that coordinates controllers and models."""
from typing import Any, Dict, List
from algorithms.ilc_controller import ILCController
from algorithms.rmpc_controller import RMPCController


class DecisionEngine:
    def __init__(self) -> None:
        self.ilc = ILCController()
        self.rmpc = RMPCController()
        self.history: List[Dict[str, Any]] = []

    def ingest_feedback(self, feedback: Dict[str, Any]) -> None:
        self.history.append(feedback)

    def make_decision(self, current_state: Dict[str, Any], reference: Dict[str, Any]) -> Dict[str, Any]:
        # Get RMPC plan
        plan = self.rmpc.plan(current_state)
        # Use ILC to adjust based on history and reference
        adj = self.ilc.update(self.history, reference)
        decision = {
            "plan": plan,
            "adjustment": adj,
        }
        return decision


__all__ = ["DecisionEngine"]
