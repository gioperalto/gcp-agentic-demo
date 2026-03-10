"""
Experiment: Marcus — Luxury Accommodation Specialist

Tests Marcus's ability to recommend luxury hotels, villas, and high-end
properties across all six destination countries.
"""

import asyncio
from typing import Dict, Any

from ddtrace.llmobs import LLMObs

from experiments.config import init_llmobs, COUNTRIES
from experiments.evaluators import (
    contains_links,
    link_count,
    mentions_destination,
    response_not_empty,
    no_external_booking_sites,
    premium_focus,
    introduces_self,
    avg_link_count,
    pass_rate_links,
)

# ── Dataset ───────────────────────────────────────────────────────────

MARCUS_DATASET_NAME = "marcus-accommodations-eval"
MARCUS_DATASET_DESC = (
    "Evaluation dataset for Marcus, the Luxury Accommodation Specialist. "
    "Tests property recommendations across countries, property types, and "
    "amenity-specific requests."
)

MARCUS_RECORDS = [
    {
        "input_data": {
            "query": "I need a 5-star hotel in Buenos Aires for a week. Something truly luxurious.",
            "destination": "Argentina",
        },
        "expected_output": {"agent_name": "Marcus", "country": "Argentina"},
        "metadata": {"category": "luxury_hotel", "country": "Argentina"},
    },
    {
        "input_data": {
            "query": "Find me a private villa in Rio de Janeiro with an ocean view.",
            "destination": "Brazil",
        },
        "expected_output": {"agent_name": "Marcus", "country": "Brazil"},
        "metadata": {"category": "villa", "country": "Brazil"},
    },
    {
        "input_data": {
            "query": "What luxury accommodations do you have in Mexico City? I'd love a hotel with a spa.",
            "destination": "Mexico",
        },
        "expected_output": {"agent_name": "Marcus", "country": "Mexico"},
        "metadata": {"category": "amenity_request", "country": "Mexico"},
    },
    {
        "input_data": {
            "query": "Show me the best hotels in Tokyo — 4.5 stars or above.",
            "destination": "Japan",
        },
        "expected_output": {"agent_name": "Marcus", "country": "Japan"},
        "metadata": {"category": "high_rating", "country": "Japan"},
    },
    {
        "input_data": {
            "query": "I'm looking for a luxury villa in Barcelona for a group of 8.",
            "destination": "Spain",
        },
        "expected_output": {"agent_name": "Marcus", "country": "Spain"},
        "metadata": {"category": "group_villa", "country": "Spain"},
    },
    {
        "input_data": {
            "query": "What's the finest hotel you can recommend in Rome? Butler service preferred.",
            "destination": "Italy",
        },
        "expected_output": {"agent_name": "Marcus", "country": "Italy"},
        "metadata": {"category": "butler_service", "country": "Italy"},
    },
    # Edge case: vague request
    {
        "input_data": {
            "query": "I want to stay somewhere amazing in Japan.",
            "destination": "Japan",
        },
        "expected_output": {"agent_name": "Marcus", "country": "Japan"},
        "metadata": {"category": "vague_request"},
    },
    # Multi-night request
    {
        "input_data": {
            "query": "I need a luxury hotel in São Paulo for a 3-night stay, checking in December 15th.",
            "destination": "Brazil",
        },
        "expected_output": {"agent_name": "Marcus", "country": "Brazil"},
        "metadata": {"category": "specific_dates"},
    },
]


# ── Task ──────────────────────────────────────────────────────────────

def marcus_task(input_data: Dict[str, Any], config: Dict[str, Any] = None) -> str:
    """Run Marcus (accommodation agent) against a user query."""
    from google.adk.runners import InMemoryRunner
    from google.genai import types
    from tribune_concierge.agent import accomadation_agent

    runner = InMemoryRunner(agent=accomadation_agent, app_name="marcus-experiment")
    session_id = f"marcus-eval-{hash(input_data['query']) & 0xFFFF:04x}"

    async def _run():
        existing = await runner.session_service.get_session(
            app_name="marcus-experiment", user_id=session_id, session_id=session_id,
        )
        if existing is None:
            await runner.session_service.create_session(
                app_name="marcus-experiment", user_id=session_id, session_id=session_id,
            )

        parts = []
        async for event in runner.run_async(
            user_id=session_id,
            session_id=session_id,
            new_message=types.Content(
                role="user", parts=[types.Part(text=input_data["query"])]
            ),
        ):
            if hasattr(event, "content") and event.content:
                if hasattr(event.content, "role") and event.content.role == "user":
                    continue
                if hasattr(event.content, "parts") and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, "text") and part.text:
                            parts.append(part.text)
        return "\n".join(parts) if parts else ""

    return asyncio.run(_run())


# ── Run ───────────────────────────────────────────────────────────────

def run():
    init_llmobs()

    dataset = LLMObs.create_dataset(
        dataset_name=MARCUS_DATASET_NAME,
        description=MARCUS_DATASET_DESC,
        records=MARCUS_RECORDS,
    )

    experiment = LLMObs.experiment(
        name="marcus-accommodation-specialist-eval",
        dataset=dataset,
        task=marcus_task,
        evaluators=[
            contains_links,
            link_count,
            mentions_destination,
            response_not_empty,
            no_external_booking_sites,
            premium_focus,
            introduces_self,
        ],
        summary_evaluators=[avg_link_count, pass_rate_links],
        description=(
            "Evaluates Marcus's luxury accommodation recommendations "
            "across all destination countries, verifying link formatting, "
            "luxury focus, amenity handling, and group capacity."
        ),
    )

    results = experiment.run(jobs=2)
    print(f"\nMarcus experiment complete. View results: {experiment.url}")
    return results


if __name__ == "__main__":
    run()
