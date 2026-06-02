"""
Experiment: Jenny — Gemini Model Comparison

Simulates Jenny's premium flight search operations across five Gemini models
to compare cost, session duration, token count, quality, and response latency.

Models evaluated:
  - gemini-3.1-pro-preview     (Gemini 3.1 Pro Preview)
  - gemini-3-flash-preview      (Gemini 3 Flash Preview)
  - gemini-3.1-flash-lite       (Gemini 3.1 Flash-Lite)
  - gemini-2.5-pro              (Gemini 2.5 Pro)
  - gemini-2.5-flash            (Gemini 2.5 Flash)
"""

import asyncio
import os
import time
from typing import Any, Dict

from ddtrace.llmobs import LLMObs
from ddtrace.llmobs._experiment import EvaluationResult as EvaluatorResult

from experiments.config import init_llmobs
from experiments.evaluators import (
    avg_link_count,
    contains_links,
    introduces_self,
    link_count,
    mentions_destination,
    no_external_booking_sites,
    pass_rate_links,
    premium_focus,
    response_not_empty,
)
from experiments.jenny_flights import JENNY_DATASET_DESC, JENNY_DATASET_NAME, JENNY_RECORDS

# ── Model registry ────────────────────────────────────────────────────
# Pricing is per 1,000 tokens (approximate public rates).
# Gemini 3.x rates are estimated based on model tier positioning.
MODELS: Dict[str, Dict[str, Any]] = {
    "gemini-3.1-pro-preview": {
        "display": "Gemini 3.1 Pro (Preview)",
        "vertex_id": "projects/datadog-community/locations/global/publishers/google/models/gemini-3.1-pro-preview",
        "input_cost_per_1k": 0.002,   # ~$2/M tokens (estimated)
        "output_cost_per_1k": 0.012,  # ~$12.00/M tokens (estimated)
    },
    "gemini-3-flash-preview": {
        "display": "Gemini 3 Flash (Preview)",
        "vertex_id": "projects/datadog-community/locations/global/publishers/google/models/gemini-3-flash-preview",
        "input_cost_per_1k": 0.0005,  # ~$0.5/M tokens (estimated)
        "output_cost_per_1k": 0.003, # ~$3.00/M tokens (estimated)
    },
    "gemini-3.1-flash-lite": {
        "display": "Gemini 3.1 Flash-Lite",
        "vertex_id": "projects/datadog-community/locations/global/publishers/google/models/gemini-3.1-flash-lite",
        "input_cost_per_1k": 0.00025, # ~$0.25/M tokens (estimated)
        "output_cost_per_1k": 0.0015, # ~$1.50/M tokens (estimated)
    },
    "gemini-2.5-pro": {
        "display": "Gemini 2.5 Pro",
        "input_cost_per_1k": 0.00125,   # $1.25/M tokens
        "output_cost_per_1k": 0.01000,  # $10.00/M tokens
    },
    "gemini-2.5-flash": {
        "display": "Gemini 2.5 Flash",
        "input_cost_per_1k": 0.0003,  # $0.30/M tokens
        "output_cost_per_1k": 0.0025, # $2.50/M tokens
    },
    "gemini-2.5-flash-lite": {
        "display": "Gemini 2.5 Flash-Lite",
        "input_cost_per_1k": 0.0001,  # $0.10/M tokens
        "output_cost_per_1k": 0.0004, # $0.40/M tokens
    },
}

# Tokens-per-character heuristic (average for English + structured output)
_CHARS_PER_TOKEN = 4.0

# Module-level timing store: keyed by (model_id, query_hash)
_timings: Dict[str, float] = {}


# ── Agent factory ─────────────────────────────────────────────────────

def _build_jenny_agent(model_id: str, vertex_id: str = None):
    """Construct a Jenny flight-search agent configured for the given model."""
    from google.adk.agents.llm_agent import Agent
    from google.adk.tools import FunctionTool
    from tribune_concierge.tools.jenny import (
        compare_flight_prices,
        get_flight_details,
        search_flights,
    )

    return Agent(
        model=vertex_id or model_id,
        name="Jenny",
        description="Agent specialized in searching premium flights for Tribune cardholders.",
        instruction="""You are Jenny, the Premium Flight Agent for Tribune cardholders. You specialize in finding exceptional flight experiences with an emphasis on business and first class travel.

WHEN TO INTRODUCE YOURSELF:
- Introduce yourself as Jenny when you first interact with a user
- After introducing yourself, immediately proceed to help with their flight-related request

WHEN TO TRANSFER TO OTHER AGENTS:
- Transfer to Marcus if the user asks about accommodations or hotels
- Transfer to Sofia if the user asks about itineraries, experiences, or activities
- Transfer to Luca if the user asks about restaurants or dining

HOW TO SEARCH FOR FLIGHTS:
1. Use the search_flights tool to find flights from our curated collection
   - Prioritize business and first class options for Tribune cardholders
   - Look for premium airlines like Delta, ANA, JAL, Iberia, and LATAM
   - Consider nonstop flights when available for optimal convenience
2. Present findings with clickable links in this format:
   - Use markdown links: [Airline FlightNumber - Class](/flights?id=FLIGHT_ID)
   - Example: **[Delta DL1025 - Business](/flights?id=flt-arg-003)**
3. Use compare_flight_prices to help users compare multiple options
4. Use get_flight_details to show comprehensive information about a specific flight

IMPORTANT NOTES:
- Always use data from the local flight database through the tools
- Include clickable links to each flight using the format: /flights?id=FLIGHT_ID
- These links will keep users in the concierge chat interface
- Give customers wide berth - do NOT assume financial restrictions
- Emphasize premium options (business/first class) but show all available classes
- Present the message field from tool responses VERBATIM to preserve links
- Never suggest external booking sites - all bookings happen through our platform""",
        tools=[
            FunctionTool(search_flights),
            FunctionTool(compare_flight_prices),
            FunctionTool(get_flight_details),
        ],
    )


# ── Task factory ──────────────────────────────────────────────────────

def make_jenny_task(model_id: str, vertex_id: str = None):
    """Return a task function that runs Jenny with the specified Gemini model."""

    def task(input_data: Dict[str, Any], config: Dict[str, Any] = None) -> str:
        from google.adk.runners import InMemoryRunner
        from google.genai import types

        agent = _build_jenny_agent(model_id, vertex_id=vertex_id)
        app_name = f"jenny-model-cmp-{model_id}"
        runner = InMemoryRunner(agent=agent, app_name=app_name)
        session_id = f"jenny-cmp-{model_id[:8]}-{hash(input_data['query']) & 0xFFFF:04x}"

        async def _run():
            existing = await runner.session_service.get_session(
                app_name=app_name, user_id=session_id, session_id=session_id
            )
            if existing is None:
                await runner.session_service.create_session(
                    app_name=app_name, user_id=session_id, session_id=session_id
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

        t0 = time.perf_counter()
        result = asyncio.run(_run())
        elapsed = time.perf_counter() - t0

        timing_key = f"{model_id}::{hash(input_data['query'])}"
        _timings[timing_key] = elapsed

        return result

    task.__name__ = f"jenny_task_{model_id.replace('-', '_').replace('.', '_')}"
    return task


# ── Per-model evaluator factories ─────────────────────────────────────

def make_latency_evaluator(model_id: str):
    """Return a response_latency evaluator scoped to a model."""

    def response_latency(input_data, output_data, expected_output):
        key = f"{model_id}::{hash(input_data['query'])}"
        latency = _timings.get(key, 0.0)
        assessment = "pass" if latency < 30.0 else "fail"
        return EvaluatorResult(
            value=latency,
            reasoning=f"Response time: {latency:.2f}s",
            assessment=assessment,
            tags={"evaluator": "response_latency", "model": model_id},
        )

    response_latency.__name__ = "response_latency"
    return response_latency


def make_token_count_evaluator(model_id: str):
    """Return an approx_output_tokens evaluator scoped to a model."""

    def approx_output_tokens(input_data, output_data, expected_output):
        est = len(output_data) / _CHARS_PER_TOKEN
        return EvaluatorResult(
            value=round(est, 1),
            reasoning=f"~{int(est)} output tokens estimated from {len(output_data)} chars",
            assessment="pass",
            tags={"evaluator": "approx_output_tokens", "model": model_id},
        )

    approx_output_tokens.__name__ = "approx_output_tokens"
    return approx_output_tokens


def make_cost_evaluator(model_id: str):
    """Return an estimated_cost_usd evaluator scoped to a model."""
    rates = MODELS[model_id]
    input_rate = rates["input_cost_per_1k"]
    output_rate = rates["output_cost_per_1k"]

    def estimated_cost_usd(input_data, output_data, expected_output):
        input_tokens = len(input_data.get("query", "")) / _CHARS_PER_TOKEN
        output_tokens = len(output_data) / _CHARS_PER_TOKEN
        cost = (input_tokens / 1000 * input_rate) + (output_tokens / 1000 * output_rate)
        return EvaluatorResult(
            value=round(cost, 6),
            reasoning=(
                f"~{int(input_tokens)} in + ~{int(output_tokens)} out tokens "
                f"@ ${input_rate}/1k in / ${output_rate}/1k out"
            ),
            assessment="pass",
            tags={"evaluator": "estimated_cost_usd", "model": model_id},
        )

    estimated_cost_usd.__name__ = "estimated_cost_usd"
    return estimated_cost_usd


# ── Summary evaluators ────────────────────────────────────────────────

def avg_latency(inputs, outputs, expected_outputs, evaluators_results):
    """Average response latency across all records (seconds)."""
    values = evaluators_results.get("response_latency", [])
    if not values:
        return 0.0
    nums = [v.value if hasattr(v, "value") else float(v) for v in values]
    return round(sum(nums) / len(nums), 3)


def total_estimated_cost(inputs, outputs, expected_outputs, evaluators_results):
    """Sum of estimated cost (USD) across all records in this experiment run."""
    values = evaluators_results.get("estimated_cost_usd", [])
    if not values:
        return 0.0
    nums = [v.value if hasattr(v, "value") else float(v) for v in values]
    return round(sum(nums), 6)


def avg_output_tokens(inputs, outputs, expected_outputs, evaluators_results):
    """Average approximate output token count across all records."""
    values = evaluators_results.get("approx_output_tokens", [])
    if not values:
        return 0.0
    nums = [v.value if hasattr(v, "value") else float(v) for v in values]
    return round(sum(nums) / len(nums), 1)


# ── Run ───────────────────────────────────────────────────────────────

def run():
    """Run one experiment per model and print a comparison table."""
    init_llmobs()

    # Shared dataset across all model experiments
    dataset = LLMObs.create_dataset(
        dataset_name=JENNY_DATASET_NAME,
        description=JENNY_DATASET_DESC,
        records=JENNY_RECORDS,
    )

    summary_rows = []

    for model_id, meta in MODELS.items():
        display = meta["display"]
        exp_name = f"jenny-model-cmp-{model_id}"

        print(f"\n{'─' * 60}")
        print(f"Running: {display}  ({model_id})")
        print(f"{'─' * 60}")

        latency_eval = make_latency_evaluator(model_id)
        token_eval = make_token_count_evaluator(model_id)
        cost_eval = make_cost_evaluator(model_id)

        vertex_id = meta.get("vertex_id")
        experiment = LLMObs.experiment(
            name=exp_name,
            dataset=dataset,
            task=make_jenny_task(model_id, vertex_id=vertex_id),
            evaluators=[
                # Quality evaluators
                contains_links,
                link_count,
                mentions_destination,
                response_not_empty,
                no_external_booking_sites,
                premium_focus,
                introduces_self,
                # Performance evaluators
                latency_eval,
                token_eval,
                cost_eval,
            ],
            summary_evaluators=[
                avg_link_count,
                pass_rate_links,
                avg_latency,
                total_estimated_cost,
                avg_output_tokens,
            ],
            description=(
                f"Model comparison experiment: Jenny running on {display}. "
                "Evaluates flight search quality, response latency, "
                "approximate token usage, and estimated cost per query."
            ),
            tags={
                "model": model_id,
                "experiment_type": "model_comparison",
                "agent": "jenny",
                "workflow": "plan_flights",
            },
        )

        try:
            results = experiment.run(jobs=1)  # serial to avoid event-loop conflicts
            summary_rows.append({
                "model": display,
                "model_id": model_id,
                "url": getattr(experiment, "url", "n/a"),
                "results": results,
            })
            print(f"  Done. Results: {getattr(experiment, 'url', 'n/a')}")
        except Exception as exc:
            print(f"  ERROR: {exc}")
            summary_rows.append({
                "model": display,
                "model_id": model_id,
                "url": "error",
                "error": str(exc),
            })

    # ── Print comparison table ─────────────────────────────────────────
    print(f"\n{'=' * 72}")
    print("Jenny — Gemini Model Comparison Summary")
    print(f"{'=' * 72}")
    print(f"{'Model':<30}  {'Experiment URL'}")
    print(f"{'─' * 30}  {'─' * 40}")
    for row in summary_rows:
        status = row.get("url", row.get("error", "n/a"))
        print(f"{row['model']:<30}  {status}")
    print(f"{'=' * 72}")
    print("\nView all experiments in Datadog:")
    print("  APM → LLM Observability → Experiments → Project: Travel Planner")
    print(f"{'=' * 72}")

    return summary_rows


if __name__ == "__main__":
    run()
