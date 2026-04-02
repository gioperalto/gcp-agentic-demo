#!/usr/bin/env python3
"""
Run all specialist experiments.

Usage:
    # Run all experiments
    python -m experiments.run_all

    # Run a single specialist by color name
    python -m experiments.run_all --agent red
    python -m experiments.run_all --agent blue
    python -m experiments.run_all --agent yellow
    python -m experiments.run_all --agent green
    python -m experiments.run_all --agent orange
    python -m experiments.run_all --agent purple
    python -m experiments.run_all --agent gray

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
        choices=["red", "blue", "yellow", "green", "orange", "purple", "gray", "hallucination", "all"],
        default="all",
        help="Which specialist to evaluate (default: all)",
    )
    args = parser.parse_args()

    runners = {
        "red": ("Red (Flights — Jenny)", "experiments.red_flights"),
        "blue": ("Blue (Accommodations — Marcus)", "experiments.blue_accommodations"),
        "yellow": ("Yellow (Experiences — Sofia)", "experiments.yellow_experiences"),
        "green": ("Green (Restaurants — Luca)", "experiments.green_restaurants"),
        "orange": ("Orange (Legionnaire Concierge)", "experiments.orange_legionnaire"),
        "purple": ("Purple (Insecure Concierge)", "experiments.purple_insecure"),
        "gray": ("Gray (Utility Infielder — Ralph)", "experiments.gray_ralph"),
        "hallucination": ("Hallucination Detection (LLM-as-Judge)", "experiments.hallucination_experiment"),
    }

    agents_to_run = list(runners.keys()) if args.agent == "all" else [args.agent]

    print("=" * 60)
    print("Datadog LLM Observability — Travel Planner Experiments")
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
    print(f"Project: Travel Planner")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
