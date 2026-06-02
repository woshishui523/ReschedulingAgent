"""Integration-like test simulating a tiny decision flow."""
from services.decision_engine import DecisionEngine
from utils.fuzzy_passenger_flow import compute_passenger_flow


def test_decision_flow_with_passenger_flow():
    counts = [10, 20, 30]
    stats = compute_passenger_flow(counts)
    engine = DecisionEngine()
    engine.ingest_feedback({"error": stats["mean"]})
    decision = engine.make_decision({"state": 0}, {"target": 1})
    assert isinstance(decision, dict)
