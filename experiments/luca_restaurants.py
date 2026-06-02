"""
Experiment: Luca — Fine Dining Specialist

Tests Luca's ability to recommend high-end restaurants, provide wine
pairing expertise, and cover all six destination countries.
"""

import asyncio
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

# ── Luca-specific evaluators ──────────────────────────────────────────

def wine_knowledge(input_data, output_data, expected_output):
    """For wine-related queries, check that Luca demonstrates sommelier expertise."""
    query = input_data.get("query", "").lower()
    if "wine" not in query and "pairing" not in query and "sommelier" not in query:
        return True  # Not a wine query
    wine_terms = [
        "wine", "pairing", "vintage", "region", "grape", "varietal",
        "tannin", "acidity", "body", "malbec", "cabernet", "tempranillo",
        "sangiovese", "pinot", "chardonnay", "rioja", "mendoza", "tuscany",
        "bordeaux", "burgundy", "napa", "barolo", "chianti",
    ]
    lower_output = output_data.lower()
    hits = [t for t in wine_terms if t in lower_output]
    score = min(len(hits) / 3.0, 1.0)
    return EvaluatorResult(
        value=score,
        reasoning=f"Wine terms found: {hits}" if hits else "No wine expertise demonstrated",
        assessment="pass" if score >= 0.33 else "fail",
        tags={"evaluator": "wine_knowledge"},
    )


def cuisine_relevance(input_data, output_data, expected_output):
    """Check that recommended cuisines match the destination country."""
    country = expected_output.get("country", "")
    expected_cuisines = {
        "Argentina": ["argentine", "steak", "asado", "empanada", "parrilla"],
        "Brazil": ["brazilian", "churrasco", "feijoada", "seafood"],
        "Mexico": ["mexican", "taco", "mole", "mezcal", "tequila"],
        "Japan": ["japanese", "sushi", "ramen", "kaiseki", "omakase", "tempura"],
        "Spain": ["spanish", "tapas", "paella", "basque", "catalan"],
        "Italy": ["italian", "pasta", "risotto", "trattoria", "osteria", "tuscan"],
    }
    terms = expected_cuisines.get(country, [])
    if not terms:
        return True
    lower_output = output_data.lower()
    hits = [t for t in terms if t in lower_output]
    found = len(hits) > 0
    return EvaluatorResult(
        value=found,
        reasoning=f"Cuisine terms for {country} found: {hits}" if found else f"No {country} cuisine terms found",
        assessment="pass" if found else "fail",
        tags={"evaluator": "cuisine_relevance"},
    )


def mentions_reservations(input_data, output_data, expected_output):
    """Check that Luca mentions reservation availability."""
    reservation_terms = ["reservation", "book", "reserve", "walk-in", "seating"]
    lower_output = output_data.lower()
    found = any(t in lower_output for t in reservation_terms)
    return EvaluatorResult(
        value=found,
        reasoning="Reservation info provided" if found else "No reservation info found",
        assessment="pass" if found else "neutral",
        tags={"evaluator": "mentions_reservations"},
    )


# ── Dataset ───────────────────────────────────────────────────────────

LUCA_DATASET_NAME = "luca-restaurants-eval"
LUCA_DATASET_DESC = (
    "Evaluation dataset for Luca, the Fine Dining Specialist. "
    "Tests restaurant recommendations, wine expertise, cuisine matching, "
    "and coverage across all six destination countries."
)

LUCA_RECORDS = [
    {
        "input_data": {
            "query": "Recommend the best steakhouses in Buenos Aires. I want a true Argentine parrilla experience.",
            "destination": "Argentina",
        },
        "expected_output": {"agent_name": "Luca", "country": "Argentina"},
        "metadata": {"category": "cuisine_specific", "country": "Argentina"},
    },
    {
        "input_data": {
            "query": "What fine dining options are there in São Paulo? I'm celebrating an anniversary.",
            "destination": "Brazil",
        },
        "expected_output": {"agent_name": "Luca", "country": "Brazil"},
        "metadata": {"category": "special_occasion", "country": "Brazil"},
    },
    {
        "input_data": {
            "query": "I'd love to try authentic high-end Mexican cuisine in Mexico City. Any recommendations?",
            "destination": "Mexico",
        },
        "expected_output": {"agent_name": "Luca", "country": "Mexico"},
        "metadata": {"category": "authentic_cuisine", "country": "Mexico"},
    },
    {
        "input_data": {
            "query": "Find me an omakase or kaiseki restaurant in Tokyo — money is no object.",
            "destination": "Japan",
        },
        "expected_output": {"agent_name": "Luca", "country": "Japan"},
        "metadata": {"category": "luxury_dining", "country": "Japan"},
    },
    {
        "input_data": {
            "query": "What Michelin-quality restaurants do you have in Barcelona?",
            "destination": "Spain",
        },
        "expected_output": {"agent_name": "Luca", "country": "Spain"},
        "metadata": {"category": "michelin", "country": "Spain"},
    },
    {
        "input_data": {
            "query": "Recommend the best Italian restaurants in Rome — traditional Tuscan cuisine preferred.",
            "destination": "Italy",
        },
        "expected_output": {"agent_name": "Luca", "country": "Italy"},
        "metadata": {"category": "regional_cuisine", "country": "Italy"},
    },
    # Wine pairing query (tests sommelier expertise)
    {
        "input_data": {
            "query": "I'm having steak in Mendoza tonight. What wine pairing would you recommend?",
            "destination": "Argentina",
        },
        "expected_output": {"agent_name": "Luca", "country": "Argentina"},
        "metadata": {"category": "wine_pairing"},
    },
    # Multi-criteria request
    {
        "input_data": {
            "query": "I want a restaurant in Tokyo with a great wine list and private dining for 6 people.",
            "destination": "Japan",
        },
        "expected_output": {"agent_name": "Luca", "country": "Japan"},
        "metadata": {"category": "multi_criteria"},
    },
]


# ── Task ──────────────────────────────────────────────────────────────

def luca_task(input_data: Dict[str, Any], config: Dict[str, Any] = None) -> str:
    """Run Luca (restaurant agent) against a user query."""
    from google.adk.runners import InMemoryRunner
    from google.genai import types
    from tribune_concierge.agent import restaurant_agent

    runner = InMemoryRunner(agent=restaurant_agent, app_name="luca-experiment")
    session_id = f"luca-eval-{hash(input_data['query']) & 0xFFFF:04x}"

    async def _run():
        existing = await runner.session_service.get_session(
            app_name="luca-experiment", user_id=session_id, session_id=session_id,
        )
        if existing is None:
            await runner.session_service.create_session(
                app_name="luca-experiment", user_id=session_id, session_id=session_id,
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
        dataset_name=LUCA_DATASET_NAME,
        description=LUCA_DATASET_DESC,
        records=LUCA_RECORDS,
    )

    experiment = LLMObs.experiment(
        name="luca-fine-dining-specialist-eval",
        dataset=dataset,
        task=luca_task,
        evaluators=[
            contains_links,
            link_count,
            mentions_destination,
            response_not_empty,
            no_external_booking_sites,
            premium_focus,
            introduces_self,
            wine_knowledge,
            cuisine_relevance,
            mentions_reservations,
        ],
        summary_evaluators=[avg_link_count, pass_rate_links],
        description=(
            "Evaluates Luca's fine dining recommendations, wine pairing "
            "expertise, cuisine relevance to destination, reservation "
            "info, and luxury focus across all countries."
        ),
    )

    results = experiment.run(jobs=2)
    print(f"\nLuca experiment complete. View results: {experiment.url}")
    return results


if __name__ == "__main__":
    run()
