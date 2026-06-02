"""Basic unit tests for the DecisionEngine."""
from services.decision_engine import DecisionEngine


def test_make_decision_returns_plan_and_adjustment():
    engine = DecisionEngine()
    engine.ingest_feedback({"error": 2.0})
    decision = engine.make_decision({"state": 0}, {"target": 1})
    assert "plan" in decision
    assert "adjustment" in decision
