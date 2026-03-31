"""
Experiment: Orange — Legionnaire Concierge (budget-focused)

Tests the Legionnaire concierge agent's ability to recommend affordable travel
options, provide clickable links, and stay within the budget tier.
"""

import asyncio
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
    avg_link_count,
    pass_rate_links,
)

# -- Domain evaluators ---------------------------------------------------------

def budget_focus(input_data, output_data, expected_output):
    """Check the response emphasises affordable / budget options."""
    budget_terms = [
        "affordable", "budget", "value", "economical", "deal", "save",
        "hostel", "economy", "mid-range", "inexpensive", "cheap",
        "low-cost", "bargain", "price", "$",
    ]
    lower_output = output_data.lower()
    hits = [t for t in budget_terms if t in lower_output]
    score = min(len(hits) / 3.0, 1.0)
    return EvaluatorResult(
        value=score,
        reasoning=f"Budget terms found: {hits}" if hits else "No budget terms found",
        assessment="pass" if score >= 0.33 else "fail",
        tags={"evaluator": "budget_focus"},
    )


def no_luxury_upsell(input_data, output_data, expected_output):
    """Verify the agent does NOT push luxury options to a Legionnaire cardholder."""
    luxury_terms = [
        "5-star", "five-star", "first class", "business class",
        "villa", "michelin", "exclusive penthouse",
    ]
    lower_output = output_data.lower()
    violations = [t for t in luxury_terms if t in lower_output]
    return EvaluatorResult(
        value=len(violations) == 0,
        reasoning="No luxury upsell detected" if not violations else f"Luxury terms found: {violations}",
        assessment="pass" if not violations else "fail",
        tags={"evaluator": "no_luxury_upsell"},
    )


def includes_prices(input_data, output_data, expected_output):
    """Check that the response includes explicit price information."""
    import re
    price_pattern = r"\$\d+"
    found = bool(re.search(price_pattern, output_data))
    return EvaluatorResult(
        value=found,
        reasoning="Price info found" if found else "No price info found",
        assessment="pass" if found else "fail",
        tags={"evaluator": "includes_prices"},
    )


# -- Dataset -------------------------------------------------------------------

ORANGE_DATASET_NAME = "orange-legionnaire-eval"
ORANGE_DATASET_DESC = (
    "Evaluation dataset for Orange (Legionnaire concierge). "
    "Tests budget-focused travel search across all six destination countries."
)

ORANGE_RECORDS = [
    {
        "input_data": {
            "query": "I'm looking for an affordable hostel in Buenos Aires.",
            "destination": "Argentina",
        },
        "expected_output": {"country": "Argentina"},
        "metadata": {"category": "accommodation_search", "country": "Argentina"},
    },
    {
        "input_data": {
            "query": "Find me cheap flights to Tokyo from San Francisco.",
            "destination": "Japan",
        },
        "expected_output": {"country": "Japan"},
        "metadata": {"category": "flight_search", "country": "Japan"},
    },
    {
        "input_data": {
            "query": "What are some budget restaurants in Barcelona?",
            "destination": "Spain",
        },
        "expected_output": {"country": "Spain"},
        "metadata": {"category": "restaurant_search", "country": "Spain"},
    },
    {
        "input_data": {
            "query": "Show me affordable things to do in Rome.",
            "destination": "Italy",
        },
        "expected_output": {"country": "Italy"},
        "metadata": {"category": "experience_search", "country": "Italy"},
    },
    {
        "input_data": {
            "query": "I need budget-friendly accommodation and flights to São Paulo.",
            "destination": "Brazil",
        },
        "expected_output": {"country": "Brazil"},
        "metadata": {"category": "multi_search", "country": "Brazil"},
    },
    {
        "input_data": {
            "query": "What economy flights go to Mexico City from Houston?",
            "destination": "Mexico",
        },
        "expected_output": {"country": "Mexico"},
        "metadata": {"category": "flight_search", "country": "Mexico"},
    },
    {
        "input_data": {
            "query": "Find me the cheapest Airbnb in Kyoto under $80 a night.",
            "destination": "Japan",
        },
        "expected_output": {"country": "Japan"},
        "metadata": {"category": "price_constrained"},
    },
    {
        "input_data": {
            "query": "What free or low-cost experiences can I enjoy in Buenos Aires?",
            "destination": "Argentina",
        },
        "expected_output": {"country": "Argentina"},
        "metadata": {"category": "budget_experience"},
    },
]


# -- Task ----------------------------------------------------------------------

def orange_task(input_data: Dict[str, Any], config: Dict[str, Any] = None) -> str:
    """Run the Legionnaire concierge against a user query."""
    from google.adk.runners import InMemoryRunner
    from google.genai import types
    from legionnaire_concierge.agent import legionnaire_agent

    runner = InMemoryRunner(agent=legionnaire_agent, app_name="orange-experiment")
    session_id = f"orange-eval-{hash(input_data['query']) & 0xFFFF:04x}"

    async def _run():
        existing = await runner.session_service.get_session(
            app_name="orange-experiment", user_id=session_id, session_id=session_id,
        )
        if existing is None:
            await runner.session_service.create_session(
                app_name="orange-experiment", user_id=session_id, session_id=session_id,
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
        dataset_name=ORANGE_DATASET_NAME,
        description=ORANGE_DATASET_DESC,
        records=ORANGE_RECORDS,
    )

    experiment = LLMObs.experiment(
        name="orange-legionnaire-concierge-eval",
        dataset=dataset,
        task=orange_task,
        evaluators=[
            contains_links,
            link_count,
            mentions_destination,
            response_not_empty,
            no_external_booking_sites,
            budget_focus,
            no_luxury_upsell,
            includes_prices,
        ],
        summary_evaluators=[avg_link_count, pass_rate_links],
        description=(
            "Evaluates Orange (Legionnaire concierge) budget-focused travel "
            "recommendations across all destination countries."
        ),
    )

    results = experiment.run(jobs=2)
    print(f"\nOrange experiment complete. View results: {experiment.url}")
    return results


if __name__ == "__main__":
    run()
