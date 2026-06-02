"""
Experiment: Sofia — Premium Experience Curator

Tests Sofia's ability to curate itineraries, search attractions, and
recommend premium experiences across all six destination countries.
"""

import asyncio
import re
from typing import Dict, Any

from ddtrace.llmobs import LLMObs
from ddtrace.llmobs._experiment import EvaluationResult as EvaluatorResult

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

# ── Sofia-specific evaluators ─────────────────────────────────────────

def experience_variety(input_data, output_data, expected_output):
    """Check that the response includes a variety of experience types."""
    experience_types = [
        "hiking", "yacht", "boat", "winery", "wine",
        "farm-to-table", "atv", "adventure", "cultural", "tour",
    ]
    lower_output = output_data.lower()
    hits = [t for t in experience_types if t in lower_output]
    score = min(len(hits) / 2.0, 1.0)  # 2+ types → 1.0
    return EvaluatorResult(
        value=score,
        reasoning=f"Experience types mentioned: {hits}" if hits else "No experience types found",
        assessment="pass" if score >= 0.5 else "fail",
        tags={"evaluator": "experience_variety"},
    )


def itinerary_structure(input_data, output_data, expected_output):
    """For itinerary requests, check that the response has a numbered/structured plan."""
    if "itinerary" not in input_data.get("query", "").lower():
        return True  # Not an itinerary request
    has_numbering = bool(re.search(r"\b[1-3]\.", output_data))
    return EvaluatorResult(
        value=has_numbering,
        reasoning="Itinerary has numbered structure" if has_numbering else "No numbered structure found",
        assessment="pass" if has_numbering else "fail",
        tags={"evaluator": "itinerary_structure"},
    )


# ── Dataset ───────────────────────────────────────────────────────────

SOFIA_DATASET_NAME = "sofia-experiences-eval"
SOFIA_DATASET_DESC = (
    "Evaluation dataset for Sofia, the Premium Experience Curator. "
    "Tests experience searches, itinerary creation, and diverse activity "
    "recommendations across all six countries."
)

SOFIA_RECORDS = [
    {
        "input_data": {
            "query": "What luxury experiences can I do in Buenos Aires? I love wine and fine dining.",
            "destination": "Argentina",
        },
        "expected_output": {"agent_name": "Sofia", "country": "Argentina"},
        "metadata": {"category": "experience_search", "country": "Argentina"},
    },
    {
        "input_data": {
            "query": "I want an adventurous day in Rio de Janeiro — maybe ATV riding and a boat tour.",
            "destination": "Brazil",
        },
        "expected_output": {"agent_name": "Sofia", "country": "Brazil"},
        "metadata": {"category": "adventure", "country": "Brazil"},
    },
    {
        "input_data": {
            "query": "Create a full day itinerary for me in Mexico City with premium experiences.",
            "destination": "Mexico",
        },
        "expected_output": {"agent_name": "Sofia", "country": "Mexico"},
        "metadata": {"category": "itinerary", "country": "Mexico"},
    },
    {
        "input_data": {
            "query": "I'd like to explore cultural experiences in Kyoto. What's available?",
            "destination": "Japan",
        },
        "expected_output": {"agent_name": "Sofia", "country": "Japan"},
        "metadata": {"category": "cultural", "country": "Japan"},
    },
    {
        "input_data": {
            "query": "Plan a luxury itinerary in Barcelona including a winery tour and yacht ride.",
            "destination": "Spain",
        },
        "expected_output": {"agent_name": "Sofia", "country": "Spain"},
        "metadata": {"category": "itinerary", "country": "Spain"},
    },
    {
        "input_data": {
            "query": "What farm-to-table experiences do you have in Tuscany?",
            "destination": "Italy",
        },
        "expected_output": {"agent_name": "Sofia", "country": "Italy"},
        "metadata": {"category": "farm_to_table", "country": "Italy"},
    },
    # Vague request
    {
        "input_data": {
            "query": "Surprise me with something special in Tokyo!",
            "destination": "Japan",
        },
        "expected_output": {"agent_name": "Sofia", "country": "Japan"},
        "metadata": {"category": "vague_request"},
    },
    # Multi-interest request
    {
        "input_data": {
            "query": "I enjoy hiking and winery tours. What can I do in Mendoza?",
            "destination": "Argentina",
        },
        "expected_output": {"agent_name": "Sofia", "country": "Argentina"},
        "metadata": {"category": "multi_interest"},
    },
]


# ── Task ──────────────────────────────────────────────────────────────

def sofia_task(input_data: Dict[str, Any], config: Dict[str, Any] = None) -> str:
    """Run Sofia (experience/itinerary agent) against a user query."""
    from google.adk.runners import InMemoryRunner
    from google.genai import types
    from tribune_concierge.agent import itinerary_agent

    runner = InMemoryRunner(agent=itinerary_agent, app_name="sofia-experiment")
    session_id = f"sofia-eval-{hash(input_data['query']) & 0xFFFF:04x}"

    async def _run():
        existing = await runner.session_service.get_session(
            app_name="sofia-experiment", user_id=session_id, session_id=session_id,
        )
        if existing is None:
            await runner.session_service.create_session(
                app_name="sofia-experiment", user_id=session_id, session_id=session_id,
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
        dataset_name=SOFIA_DATASET_NAME,
        description=SOFIA_DATASET_DESC,
        records=SOFIA_RECORDS,
    )

    experiment = LLMObs.experiment(
        name="sofia-experience-curator-eval",
        dataset=dataset,
        task=sofia_task,
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
            "Evaluates Sofia's experience curation and itinerary planning "
            "capabilities, verifying diverse activity types, structured "
            "itineraries, link formatting, and luxury focus."
        ),
    )

    results = experiment.run(jobs=2)
    print(f"\nSofia experiment complete. View results: {experiment.url}")
    return results


if __name__ == "__main__":
    run()
