"""
Experiment: Red — Premium Flight Specialist (formerly Jenny)

Tests the flight sub-agent's ability to search and recommend premium flights
across all six destination countries, verify link formatting, and maintain
a luxury focus.
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

RED_DATASET_NAME = "red-flights-eval"
RED_DATASET_DESC = (
    "Evaluation dataset for Red (flight sub-agent). "
    "Each record contains a user query about flights and the expected "
    "destination country and agent name."
)

RED_RECORDS = [
    {
        "input_data": {
            "query": "I'd like to fly to Buenos Aires from New York next month. What first class options do you have?",
            "destination": "Argentina",
        },
        "expected_output": {"agent_name": "Jenny", "country": "Argentina"},
        "metadata": {"category": "country_search", "country": "Argentina"},
    },
    {
        "input_data": {
            "query": "Find me business class flights to Tokyo from Los Angeles.",
            "destination": "Japan",
        },
        "expected_output": {"agent_name": "Jenny", "country": "Japan"},
        "metadata": {"category": "country_search", "country": "Japan"},
    },
    {
        "input_data": {
            "query": "What premium flights are available to Barcelona from Miami?",
            "destination": "Spain",
        },
        "expected_output": {"agent_name": "Jenny", "country": "Spain"},
        "metadata": {"category": "country_search", "country": "Spain"},
    },
    {
        "input_data": {
            "query": "I want to fly first class to Rome. What do you have from JFK?",
            "destination": "Italy",
        },
        "expected_output": {"agent_name": "Jenny", "country": "Italy"},
        "metadata": {"category": "country_search", "country": "Italy"},
    },
    {
        "input_data": {
            "query": "Show me flights to São Paulo, preferably business class on LATAM.",
            "destination": "Brazil",
        },
        "expected_output": {"agent_name": "Jenny", "country": "Brazil"},
        "metadata": {"category": "airline_preference", "country": "Brazil"},
    },
    {
        "input_data": {
            "query": "I need a direct flight to Mexico City from Dallas. Premium economy or better.",
            "destination": "Mexico",
        },
        "expected_output": {"agent_name": "Jenny", "country": "Mexico"},
        "metadata": {"category": "direct_flight", "country": "Mexico"},
    },
    {
        "input_data": {
            "query": "Compare the best first class and business class options to Buenos Aires.",
            "destination": "Argentina",
        },
        "expected_output": {"agent_name": "Jenny", "country": "Argentina"},
        "metadata": {"category": "comparison"},
    },
    {
        "input_data": {
            "query": "What's the most luxurious way to fly to Japan?",
            "destination": "Japan",
        },
        "expected_output": {"agent_name": "Jenny", "country": "Japan"},
        "metadata": {"category": "luxury_preference"},
    },
]


# -- Task ----------------------------------------------------------------------

def red_task(input_data: Dict[str, Any], config: Dict[str, Any] = None) -> str:
    """Run the flight sub-agent against a user query using the ADK runner."""
    from google.adk.runners import InMemoryRunner
    from google.genai import types
    from tribune_concierge.agent import flight_search_agent

    runner = InMemoryRunner(agent=flight_search_agent, app_name="red-experiment")
    session_id = f"red-eval-{hash(input_data['query']) & 0xFFFF:04x}"

    async def _run():
        existing = await runner.session_service.get_session(
            app_name="red-experiment", user_id=session_id, session_id=session_id,
        )
        if existing is None:
            await runner.session_service.create_session(
                app_name="red-experiment", user_id=session_id, session_id=session_id,
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
        dataset_name=RED_DATASET_NAME,
        description=RED_DATASET_DESC,
        records=RED_RECORDS,
    )

    experiment = LLMObs.experiment(
        name="red-flight-specialist-eval",
        dataset=dataset,
        task=red_task,
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
            "Evaluates Red (flight sub-agent) premium flight search capabilities "
            "across all destination countries, verifying link formatting, luxury "
            "focus, and self-introduction behaviour."
        ),
    )

    results = experiment.run(jobs=2)
    print(f"\nRed experiment complete. View results: {experiment.url}")
    return results


if __name__ == "__main__":
    run()
