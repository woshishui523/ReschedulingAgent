"""Start script that initializes DB and runs the engine once."""
from migrations.create_feedback_table import run as create_tables
from services.decision_engine import DecisionEngine


def main():
    create_tables()
    engine = DecisionEngine()
    print("Engine initialized. Ready.")


if __name__ == "__main__":
    main()
