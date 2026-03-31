"""
Experiment: Yellow — Premium Experience Curator (formerly Sofia)

Tests the experience sub-agent's ability to search premium activities,
build itineraries, and recommend diverse experiences.
"""

import asyncio
import re
from typing import Dict, Any

from ddtrace.llmobs import LLMObs
from ddtrace.llmobs._experiment import EvaluationResult as EvaluatorResult

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

# -- Domain evaluators ---------------------------------------------------------

def experience_variety(input_data, output_data, expected_output):
    """Check the response mentions a variety of experience types."""
    experience_types = [
        "hiking", "yacht", "winery", "wine", "farm-to-table", "farm to table",
        "adventure", "cultural", "atv", "boat", "cooking class", "tour",
    ]
    lower_output = output_data.lower()
    hits = [t for t in experience_types if t in lower_output]
    score = min(len(hits) / 3.0, 1.0)
    return EvaluatorResult(
        value=score,
        reasoning=f"Experience types found: {hits}" if hits else "No experience types found",
        assessment="pass" if score >= 0.33 else "fail",
        tags={"evaluator": "experience_variety"},
    )


def itinerary_structure(input_data, output_data, expected_output):
    """If the query asks for an itinerary, check for numbered structure."""
    if "itinerary" not in input_data.get("query", "").lower():
        return True
    has_numbering = bool(re.search(r"\b[1-3]\.", output_data))
    return EvaluatorResult(
        value=has_numbering,
        reasoning="Numbered itinerary structure found" if has_numbering else "No numbered structure",
        assessment="pass" if has_numbering else "fail",
        tags={"evaluator": "itinerary_structure"},
    )


# -- Dataset -------------------------------------------------------------------

YELLOW_DATASET_NAME = "yellow-experiences-eval"
YELLOW_DATASET_DESC = (
    "Evaluation dataset for Yellow (experience sub-agent). "
    "Each record contains a user query about experiences and the expected "
    "destination country and agent name."
)

YELLOW_RECORDS = [
    {
        "input_data": {
            "query": "What luxury experiences can I enjoy in Buenos Aires?",
            "destination": "Argentina",
        },
        "expected_output": {"agent_name": "Sofia", "country": "Argentina"},
        "metadata": {"category": "luxury_search", "country": "Argentina"},
    },
    {
        "input_data": {
            "query": "Create a 3-day itinerary for premium activities in Tokyo.",
            "destination": "Japan",
        },
        "expected_output": {"agent_name": "Sofia", "country": "Japan"},
        "metadata": {"category": "itinerary", "country": "Japan"},
    },
    {
        "input_data": {
            "query": "I want a private yacht tour and winery experience in Barcelona.",
            "destination": "Spain",
        },
        "expected_output": {"agent_name": "Sofia", "country": "Spain"},
        "metadata": {"category": "specific_experience", "country": "Spain"},
    },
    {
        "input_data": {
            "query": "Show me the best cultural and adventure experiences in Rome.",
            "destination": "Italy",
        },
        "expected_output": {"agent_name": "Sofia", "country": "Italy"},
        "metadata": {"category": "mixed_interests", "country": "Italy"},
    },
    {
        "input_data": {
            "query": "What farm-to-table and hiking options are available near Rio?",
            "destination": "Brazil",
        },
        "expected_output": {"agent_name": "Sofia", "country": "Brazil"},
        "metadata": {"category": "specific_experience", "country": "Brazil"},
    },
    {
        "input_data": {
            "query": "Find me ATV tours and premium activities in Cancun.",
            "destination": "Mexico",
        },
        "expected_output": {"agent_name": "Sofia", "country": "Mexico"},
        "metadata": {"category": "adventure", "country": "Mexico"},
    },
    {
        "input_data": {
            "query": "Build a day itinerary mixing hiking and fine dining in Mendoza.",
            "destination": "Argentina",
        },
        "expected_output": {"agent_name": "Sofia", "country": "Argentina"},
        "metadata": {"category": "itinerary"},
    },
    {
        "input_data": {
            "query": "What unique, once-in-a-lifetime experiences can I have in Japan?",
            "destination": "Japan",
        },
        "expected_output": {"agent_name": "Sofia", "country": "Japan"},
        "metadata": {"category": "luxury_preference"},
    },
]


# -- Task ----------------------------------------------------------------------

def yellow_task(input_data: Dict[str, Any], config: Dict[str, Any] = None) -> str:
    """Run the experience sub-agent against a user query."""
    from google.adk.runners import InMemoryRunner
    from google.genai import types
    from tribune_concierge.agent import itinerary_agent

    runner = InMemoryRunner(agent=itinerary_agent, app_name="yellow-experiment")
    session_id = f"yellow-eval-{hash(input_data['query']) & 0xFFFF:04x}"

    async def _run():
        existing = await runner.session_service.get_session(
            app_name="yellow-experiment", user_id=session_id, session_id=session_id,
        )
        if existing is None:
            await runner.session_service.create_session(
                app_name="yellow-experiment", user_id=session_id, session_id=session_id,
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
        dataset_name=YELLOW_DATASET_NAME,
        description=YELLOW_DATASET_DESC,
        records=YELLOW_RECORDS,
    )

    experiment = LLMObs.experiment(
        name="yellow-experience-curator-eval",
        dataset=dataset,
        task=yellow_task,
        evaluators=[
            contains_links,
            link_count,
            mentions_destination,
            response_not_empty,
            no_external_booking_sites,
            premium_focus,
            introduces_self,
            experience_variety,
            itinerary_structure,
        ],
        summary_evaluators=[avg_link_count, pass_rate_links],
        description=(
            "Evaluates Yellow (experience sub-agent) premium activity search "
            "and itinerary building across all destination countries."
        ),
    )

    results = experiment.run(jobs=2)
    print(f"\nYellow experiment complete. View results: {experiment.url}")
    return results


if __name__ == "__main__":
    run()
