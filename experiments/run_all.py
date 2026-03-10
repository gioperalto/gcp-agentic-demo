#!/usr/bin/env python3
"""
Run all specialist experiments.

Usage:
    # Run all experiments
    python -m experiments.run_all

    # Run a single specialist
    python -m experiments.run_all --agent jenny
    python -m experiments.run_all --agent marcus
    python -m experiments.run_all --agent sofia
    python -m experiments.run_all --agent luca

Environment variables required:
    DATADOG_API_KEY          — Datadog API key
    DD_APPLICATION_KEY       — Datadog Application key (for experiments SDK)
    GOOGLE_GENAI_MODEL       — Gemini model name (e.g. gemini-3-flash-preview)
    GOOGLE_GENAI_USE_VERTEXAI — "True" to use Vertex AI
    GOOGLE_APPLICATION_CREDENTIALS — Path to GCP service account JSON
"""

import argparse
import os
import sys

# Ensure the project root is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Set default GOOGLE_CLOUD_LOCATION for text-based agents
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")


def main():
    parser = argparse.ArgumentParser(description="Run Datadog LLM Observability Experiments")
    parser.add_argument(
        "--agent",
        choices=["jenny", "marcus", "sofia", "luca", "all"],
        default="all",
        help="Which specialist to evaluate (default: all)",
    )
    args = parser.parse_args()

    runners = {
        "jenny": ("Jenny (Flights)", "experiments.jenny_flights"),
        "marcus": ("Marcus (Accommodations)", "experiments.marcus_accommodations"),
        "sofia": ("Sofia (Experiences)", "experiments.sofia_experiences"),
        "luca": ("Luca (Restaurants)", "experiments.luca_restaurants"),
    }

    agents_to_run = list(runners.keys()) if args.agent == "all" else [args.agent]

    print("=" * 60)
    print("Datadog LLM Observability — Specialist Experiments")
    print("=" * 60)

    for agent_key in agents_to_run:
        label, module_name = runners[agent_key]
        print(f"\n{'─' * 60}")
        print(f"Running experiment: {label}")
        print(f"{'─' * 60}")
        try:
            module = __import__(module_name, fromlist=["run"])
            module.run()
        except Exception as e:
            print(f"ERROR running {label}: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'=' * 60}")
    print("All experiments complete.")
    print("View results in Datadog → LLM Observability → Experiments")
    print(f"Project: travel-planner-experiments")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
