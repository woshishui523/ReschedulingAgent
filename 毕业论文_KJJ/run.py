"""Lightweight run script to exercise the decision engine."""
from services.decision_engine import DecisionEngine


def main():
    engine = DecisionEngine()
    # example usage
    decision = engine.make_decision({"state": 0}, {"target": 1})
    print("Decision:", decision)


if __name__ == "__main__":
    main()
