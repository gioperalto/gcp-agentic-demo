"""
Experiment: Hallucination Detection — LLM-as-Judge

Runs both Legionnaire and Tribune concierge agents against a curated dataset,
captures tool results as ground truth, and uses a judge LLM to score whether
the agent's response is grounded in the retrieved data.

Usage:
    python -m experiments.hallucination_experiment
    python -m experiments.hallucination_experiment --tier legionnaire
    python -m experiments.hallucination_experiment --tier tribune
"""

import argparse
import asyncio
import json
from typing import Any, Dict

from ddtrace.llmobs import LLMObs

from experiments.config import init_llmobs
from experiments.evaluators import (
    contains_links,
    link_count,
    mentions_destination,
    response_not_empty,
    no_external_booking_sites,
    avg_link_count,
    pass_rate_links,
)
from experiments.hallucination_evaluator import hallucination_score


# ── Dataset ──────────────────────────────────────────────────────────

HALLUCINATION_DATASET_NAME = "hallucination-detection-eval"
HALLUCINATION_DATASET_DESC = (
    "Evaluation dataset for hallucination detection across Legionnaire and "
    "Tribune concierge agents.  Each record triggers tool calls whose results "
    "serve as ground truth for the LLM-as-judge."
)

# Records designed to trigger tool calls (specific, data-backed queries)
HALLUCINATION_RECORDS = [
    # ── Legionnaire (budget) ─────────────────────────────────────────
    {
        "input_data": {
            "query": "What affordable restaurants are there in Buenos Aires?",
            "destination": "Argentina",
            "tier": "legionnaire",
        },
        "expected_output": {"tier": "legionnaire", "category": "restaurants"},
        "metadata": {"tier": "legionnaire", "category": "restaurants", "country": "Argentina"},
    },
    {
        "input_data": {
            "query": "Find me budget hostels in Tokyo under $60 a night.",
            "destination": "Japan",
            "tier": "legionnaire",
        },
        "expected_output": {"tier": "legionnaire", "category": "accommodations"},
        "metadata": {"tier": "legionnaire", "category": "accommodations", "country": "Japan"},
    },
    {
        "input_data": {
            "query": "What economy flights go from JFK to Mexico City?",
            "destination": "Mexico",
            "tier": "legionnaire",
        },
        "expected_output": {"tier": "legionnaire", "category": "flights"},
        "metadata": {"tier": "legionnaire", "category": "flights", "country": "Mexico"},
    },
    {
        "input_data": {
            "query": "Show me affordable hiking experiences in Rio de Janeiro.",
            "destination": "Brazil",
            "tier": "legionnaire",
        },
        "expected_output": {"tier": "legionnaire", "category": "experiences"},
        "metadata": {"tier": "legionnaire", "category": "experiences", "country": "Brazil"},
    },
    {
        "input_data": {
            "query": "What are cheap places to eat in Barcelona?",
            "destination": "Spain",
            "tier": "legionnaire",
        },
        "expected_output": {"tier": "legionnaire", "category": "restaurants"},
        "metadata": {"tier": "legionnaire", "category": "restaurants", "country": "Spain"},
    },
    {
        "input_data": {
            "query": "Budget-friendly things to do in Rome for a day.",
            "destination": "Italy",
            "tier": "legionnaire",
        },
        "expected_output": {"tier": "legionnaire", "category": "experiences"},
        "metadata": {"tier": "legionnaire", "category": "experiences", "country": "Italy"},
    },
    # ── Tribune (premium) ────────────────────────────────────────────
    {
        "input_data": {
            "query": "I want the best luxury dining in Tokyo. Money is no object.",
            "destination": "Japan",
            "tier": "tribune",
        },
        "expected_output": {"tier": "tribune", "category": "restaurants"},
        "metadata": {"tier": "tribune", "category": "restaurants", "country": "Japan"},
    },
    {
        "input_data": {
            "query": "Find me 5-star hotels in Buenos Aires with a spa.",
            "destination": "Argentina",
            "tier": "tribune",
        },
        "expected_output": {"tier": "tribune", "category": "accommodations"},
        "metadata": {"tier": "tribune", "category": "accommodations", "country": "Argentina"},
    },
    {
        "input_data": {
            "query": "What first-class flights are available from LAX to Madrid?",
            "destination": "Spain",
            "tier": "tribune",
        },
        "expected_output": {"tier": "tribune", "category": "flights"},
        "metadata": {"tier": "tribune", "category": "flights", "country": "Spain"},
    },
    {
        "input_data": {
            "query": "Premium winery tours and yacht experiences in Italy.",
            "destination": "Italy",
            "tier": "tribune",
        },
        "expected_output": {"tier": "tribune", "category": "experiences"},
        "metadata": {"tier": "tribune", "category": "experiences", "country": "Italy"},
    },
    {
        "input_data": {
            "query": "Recommend high-end restaurants in Sao Paulo for a special occasion.",
            "destination": "Brazil",
            "tier": "tribune",
        },
        "expected_output": {"tier": "tribune", "category": "restaurants"},
        "metadata": {"tier": "tribune", "category": "restaurants", "country": "Brazil"},
    },
    {
        "input_data": {
            "query": "Luxury villa accommodations in Cancun for a family of 6.",
            "destination": "Mexico",
            "tier": "tribune",
        },
        "expected_output": {"tier": "tribune", "category": "accommodations"},
        "metadata": {"tier": "tribune", "category": "accommodations", "country": "Mexico"},
    },
]


# ── Task: run agent and capture tool context ─────────────────────────

def _run_agent_with_tool_capture(query: str, tier: str) -> tuple[str, list[str]]:
    """Run the appropriate agent and return (response_text, tool_context)."""
    from google.adk.runners import InMemoryRunner
    from google.genai import types

    if tier == "tribune":
        from tribune_concierge.agent import root_agent
        agent = root_agent
        app_name = "hallucination-tribune-eval"
    else:
        from legionnaire_concierge.agent import legionnaire_agent
        agent = legionnaire_agent
        app_name = "hallucination-legionnaire-eval"

    runner = InMemoryRunner(agent=agent, app_name=app_name)
    session_id = f"halluc-eval-{hash(query) & 0xFFFF:04x}"

    async def _run():
        existing = await runner.session_service.get_session(
            app_name=app_name, user_id=session_id, session_id=session_id,
        )
        if existing is None:
            await runner.session_service.create_session(
                app_name=app_name, user_id=session_id, session_id=session_id,
            )

        response_parts = []
        tool_results = []

        async for event in runner.run_async(
            user_id=session_id,
            session_id=session_id,
            new_message=types.Content(
                role="user", parts=[types.Part(text=query)]
            ),
        ):
            if not hasattr(event, "content") or not event.content:
                continue
            if hasattr(event.content, "role") and event.content.role == "user":
                continue
            if not hasattr(event.content, "parts") or not event.content.parts:
                continue

            for part in event.content.parts:
                if hasattr(part, "text") and part.text:
                    response_parts.append(part.text)
                elif hasattr(part, "function_response") and part.function_response:
                    try:
                        fr = part.function_response
                        resp_data = fr.response if hasattr(fr, "response") else str(fr)
                        if isinstance(resp_data, dict):
                            tool_results.append(json.dumps(resp_data, default=str))
                        else:
                            tool_results.append(str(resp_data))
                    except Exception:
                        pass

        return "\n".join(response_parts), tool_results

    return asyncio.run(_run())


def hallucination_task(input_data: Dict[str, Any], config: Dict[str, Any] = None) -> str:
    """Task function for ddtrace experiment framework.

    Runs the agent, captures tool context, and injects it back into
    ``input_data`` so the ``hallucination_score`` evaluator can use it.
    """
    query = input_data["query"]
    tier = input_data.get("tier", "legionnaire")

    response_text, tool_ctx = _run_agent_with_tool_capture(query, tier)

    # Inject tool context into input_data so the evaluator can access it
    input_data["tool_context"] = tool_ctx

    return response_text


# ── Run ──────────────────────────────────────────────────────────────

def run(tier_filter: str = "all"):
    init_llmobs()

    records = HALLUCINATION_RECORDS
    if tier_filter != "all":
        records = [r for r in records if r["input_data"]["tier"] == tier_filter]

    dataset = LLMObs.create_dataset(
        dataset_name=HALLUCINATION_DATASET_NAME,
        description=HALLUCINATION_DATASET_DESC,
        records=records,
    )

    experiment = LLMObs.experiment(
        name="hallucination-detection-llm-judge",
        dataset=dataset,
        task=hallucination_task,
        evaluators=[
            hallucination_score,
            contains_links,
            link_count,
            mentions_destination,
            response_not_empty,
            no_external_booking_sites,
        ],
        summary_evaluators=[avg_link_count, pass_rate_links],
        description=(
            "LLM-as-judge hallucination detection across Legionnaire and Tribune "
            "concierge agents. Compares agent output against tool-retrieved "
            "ground truth data to detect fabricated names, prices, ratings, or links."
        ),
    )

    results = experiment.run(jobs=2)
    print(f"\nHallucination experiment complete. View results: {experiment.url}")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run hallucination detection experiment")
    parser.add_argument(
        "--tier",
        choices=["legionnaire", "tribune", "all"],
        default="all",
        help="Which tier to evaluate (default: all)",
    )
    args = parser.parse_args()
    run(tier_filter=args.tier)
