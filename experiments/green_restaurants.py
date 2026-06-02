"""
Experiment: Green — Fine Dining Specialist (formerly Luca)

Tests the restaurant sub-agent's ability to recommend high-end restaurants,
demonstrate sommelier expertise, and match cuisine to destination.
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
    premium_focus,
    introduces_self,
    avg_link_count,
    pass_rate_links,
)

# -- Domain evaluators ---------------------------------------------------------

def wine_knowledge(input_data, output_data, expected_output):
    """Check that the agent demonstrates sommelier/wine expertise."""
    query = input_data.get("query", "").lower()
    if "wine" not in query and "pairing" not in query and "sommelier" not in query:
        return True
    wine_terms = [
        "wine", "vintage", "region", "grape", "pairing", "tannin",
        "acidity", "body", "malbec", "tempranillo", "sangiovese",
        "chianti", "rioja", "barolo", "cabernet", "merlot",
    ]
    lower_output = output_data.lower()
    hits = [t for t in wine_terms if t in lower_output]
    score = min(len(hits) / 3.0, 1.0)
    return EvaluatorResult(
        value=score,
        reasoning=f"Wine terms found: {hits}" if hits else "No wine terms found",
        assessment="pass" if score >= 0.33 else "fail",
        tags={"evaluator": "wine_knowledge"},
    )


def cuisine_relevance(input_data, output_data, expected_output):
    """Verify cuisine matches the destination country."""
    country_cuisines = {
        "Argentina": ["steak", "asado", "empanada", "malbec", "parrilla"],
        "Brazil": ["churrasco", "feijoada", "brazilian", "caipirinha", "pão de queijo"],
        "Mexico": ["taco", "mole", "mezcal", "tequila", "mexican", "ceviche"],
        "Japan": ["sushi", "ramen", "kaiseki", "wagyu", "tempura", "sake", "omakase"],
        "Spain": ["tapas", "paella", "pintxos", "jamón", "rioja", "spanish"],
        "Italy": ["pasta", "risotto", "pizza", "trattoria", "italian", "osso buco"],
    }
    country = expected_output.get("country", "")
    if country not in country_cuisines:
        return True
    lower_output = output_data.lower()
    terms = country_cuisines[country]
    hits = [t for t in terms if t in lower_output]
    score = min(len(hits) / 2.0, 1.0)
    return EvaluatorResult(
        value=score,
        reasoning=f"Cuisine terms found for {country}: {hits}" if hits else f"No {country} cuisine terms",
        assessment="pass" if score >= 0.5 else "fail",
        tags={"evaluator": "cuisine_relevance"},
    )


def mentions_reservations(input_data, output_data, expected_output):
    """Check that the response mentions reservation or booking info."""
    reservation_terms = ["reservation", "reservations", "book", "booking", "reserve", "table"]
    lower_output = output_data.lower()
    found = any(t in lower_output for t in reservation_terms)
    return EvaluatorResult(
        value=found,
        reasoning="Reservation info mentioned" if found else "No reservation info found",
        assessment="pass" if found else "fail",
        tags={"evaluator": "mentions_reservations"},
    )


# -- Dataset -------------------------------------------------------------------

GREEN_DATASET_NAME = "green-restaurants-eval"
GREEN_DATASET_DESC = (
    "Evaluation dataset for Green (restaurant sub-agent). "
    "Each record contains a user query about dining and the expected "
    "destination country and agent name."
)

GREEN_RECORDS = [
    {
        "input_data": {
            "query": "Find me the best steakhouse in Buenos Aires for a special dinner.",
            "destination": "Argentina",
        },
        "expected_output": {"agent_name": "Luca", "country": "Argentina"},
        "metadata": {"category": "cuisine_search", "country": "Argentina"},
    },
    {
        "input_data": {
            "query": "I want an authentic omakase experience in Tokyo. What do you recommend?",
            "destination": "Japan",
        },
        "expected_output": {"agent_name": "Luca", "country": "Japan"},
        "metadata": {"category": "cuisine_search", "country": "Japan"},
    },
    {
        "input_data": {
            "query": "What are the best fine dining restaurants in Barcelona with wine pairings?",
            "destination": "Spain",
        },
        "expected_output": {"agent_name": "Luca", "country": "Spain"},
        "metadata": {"category": "wine_pairing", "country": "Spain"},
    },
    {
        "input_data": {
            "query": "Recommend a Michelin-quality Italian restaurant in Rome.",
            "destination": "Italy",
        },
        "expected_output": {"agent_name": "Luca", "country": "Italy"},
        "metadata": {"category": "luxury_search", "country": "Italy"},
    },
    {
        "input_data": {
            "query": "Where can I get the best churrasco in São Paulo?",
            "destination": "Brazil",
        },
        "expected_output": {"agent_name": "Luca", "country": "Brazil"},
        "metadata": {"category": "cuisine_search", "country": "Brazil"},
    },
    {
        "input_data": {
            "query": "I want upscale Mexican cuisine in Mexico City. Not touristy.",
            "destination": "Mexico",
        },
        "expected_output": {"agent_name": "Luca", "country": "Mexico"},
        "metadata": {"category": "luxury_search", "country": "Mexico"},
    },
    {
        "input_data": {
            "query": "What wine would you pair with a premium steak dinner in Mendoza?",
            "destination": "Argentina",
        },
        "expected_output": {"agent_name": "Luca", "country": "Argentina"},
        "metadata": {"category": "wine_pairing"},
    },
    {
        "input_data": {
            "query": "Suggest the most exclusive dining experience available in Kyoto.",
            "destination": "Japan",
        },
        "expected_output": {"agent_name": "Luca", "country": "Japan"},
        "metadata": {"category": "luxury_preference"},
    },
]


# -- Task ----------------------------------------------------------------------

def green_task(input_data: Dict[str, Any], config: Dict[str, Any] = None) -> str:
    """Run the restaurant sub-agent against a user query."""
    from google.adk.runners import InMemoryRunner
    from google.genai import types
    from tribune_concierge.agent import restaurant_agent

    runner = InMemoryRunner(agent=restaurant_agent, app_name="green-experiment")
    session_id = f"green-eval-{hash(input_data['query']) & 0xFFFF:04x}"

    async def _run():
        existing = await runner.session_service.get_session(
            app_name="green-experiment", user_id=session_id, session_id=session_id,
        )
        if existing is None:
            await runner.session_service.create_session(
                app_name="green-experiment", user_id=session_id, session_id=session_id,
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
        dataset_name=GREEN_DATASET_NAME,
        description=GREEN_DATASET_DESC,
        records=GREEN_RECORDS,
    )

    experiment = LLMObs.experiment(
        name="green-dining-specialist-eval",
        dataset=dataset,
        task=green_task,
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
            "Evaluates Green (restaurant sub-agent) fine dining recommendations, "
            "sommelier expertise, and cuisine relevance across all destinations."
        ),
    )

    results = experiment.run(jobs=2)
    print(f"\nGreen experiment complete. View results: {experiment.url}")
    return results


if __name__ == "__main__":
    run()
