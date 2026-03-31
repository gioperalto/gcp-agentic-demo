"""
Experiment: Blue — Luxury Accommodation Specialist (formerly Marcus)

Tests the accommodation sub-agent's ability to search and recommend luxury
properties across all six destination countries.
"""

import asyncio
from typing import Dict, Any

from ddtrace.llmobs import LLMObs

from experiments.config import init_llmobs
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

# -- Dataset -------------------------------------------------------------------

BLUE_DATASET_NAME = "blue-accommodations-eval"
BLUE_DATASET_DESC = (
    "Evaluation dataset for Blue (accommodation sub-agent). "
    "Each record contains a user query about accommodations and the expected "
    "destination country and agent name."
)

BLUE_RECORDS = [
    {
        "input_data": {
            "query": "Find me the best 5-star hotel in Buenos Aires with a spa.",
            "destination": "Argentina",
        },
        "expected_output": {"agent_name": "Marcus", "country": "Argentina"},
        "metadata": {"category": "luxury_search", "country": "Argentina"},
    },
    {
        "input_data": {
            "query": "I'm looking for a luxury villa in Tokyo with traditional Japanese design.",
            "destination": "Japan",
        },
        "expected_output": {"agent_name": "Marcus", "country": "Japan"},
        "metadata": {"category": "villa_search", "country": "Japan"},
    },
    {
        "input_data": {
            "query": "What's the most exclusive hotel in Barcelona?",
            "destination": "Spain",
        },
        "expected_output": {"agent_name": "Marcus", "country": "Spain"},
        "metadata": {"category": "luxury_search", "country": "Spain"},
    },
    {
        "input_data": {
            "query": "I need a 5-star hotel in Rome near the historic center with a rooftop restaurant.",
            "destination": "Italy",
        },
        "expected_output": {"agent_name": "Marcus", "country": "Italy"},
        "metadata": {"category": "amenity_search", "country": "Italy"},
    },
    {
        "input_data": {
            "query": "Show me luxury beachfront properties in Rio de Janeiro.",
            "destination": "Brazil",
        },
        "expected_output": {"agent_name": "Marcus", "country": "Brazil"},
        "metadata": {"category": "location_search", "country": "Brazil"},
    },
    {
        "input_data": {
            "query": "Find me a premium resort in Cancun with an infinity pool.",
            "destination": "Mexico",
        },
        "expected_output": {"agent_name": "Marcus", "country": "Mexico"},
        "metadata": {"category": "amenity_search", "country": "Mexico"},
    },
    {
        "input_data": {
            "query": "Compare the top luxury hotels in Buenos Aires for a week-long stay.",
            "destination": "Argentina",
        },
        "expected_output": {"agent_name": "Marcus", "country": "Argentina"},
        "metadata": {"category": "comparison"},
    },
    {
        "input_data": {
            "query": "What's the most prestigious place to stay in Kyoto?",
            "destination": "Japan",
        },
        "expected_output": {"agent_name": "Marcus", "country": "Japan"},
        "metadata": {"category": "luxury_preference"},
    },
]


# -- Task ----------------------------------------------------------------------

def blue_task(input_data: Dict[str, Any], config: Dict[str, Any] = None) -> str:
    """Run the accommodation sub-agent against a user query."""
    from google.adk.runners import InMemoryRunner
    from google.genai import types
    from tribune_concierge.agent import accomadation_agent

    runner = InMemoryRunner(agent=accomadation_agent, app_name="blue-experiment")
    session_id = f"blue-eval-{hash(input_data['query']) & 0xFFFF:04x}"

    async def _run():
        existing = await runner.session_service.get_session(
            app_name="blue-experiment", user_id=session_id, session_id=session_id,
        )
        if existing is None:
            await runner.session_service.create_session(
                app_name="blue-experiment", user_id=session_id, session_id=session_id,
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


# -- Run -----------------------------------------------------------------------

def run():
    init_llmobs()

    dataset = LLMObs.create_dataset(
        dataset_name=BLUE_DATASET_NAME,
        description=BLUE_DATASET_DESC,
        records=BLUE_RECORDS,
    )

    experiment = LLMObs.experiment(
        name="blue-accommodation-specialist-eval",
        dataset=dataset,
        task=blue_task,
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
            "Evaluates Blue (accommodation sub-agent) luxury property search "
            "capabilities across all destination countries."
        ),
    )

    results = experiment.run(jobs=2)
    print(f"\nBlue experiment complete. View results: {experiment.url}")
    return results


if __name__ == "__main__":
    run()
