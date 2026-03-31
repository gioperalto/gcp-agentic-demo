"""
Hallucination detection via LLM-as-judge.

Compares agent output against tool-retrieved ground truth data to detect
fabricated names, prices, ratings, IDs, or links that don't exist in the
seed data.

Two entry points:
  - ``hallucination_judge``   — inline evaluation called from main.py after
                                 each concierge turn (async, submits to LLMObs)
  - ``hallucination_score``   — experiment evaluator compatible with the
                                 ddtrace experiment framework (sync)
"""

import json
import logging
import os
import re

from google import genai

from ddtrace.llmobs import LLMObs
from ddtrace.llmobs._experiment import EvaluationResult as EvaluatorResult

logger = logging.getLogger("travel_planner")

# ── Judge model ──────────────────────────────────────────────────────
# Use the same Gemini model the agents use (fast + cheap for judging).
_JUDGE_MODEL = os.getenv("HALLUCINATION_JUDGE_MODEL", "gemini-2.0-flash")

_JUDGE_SYSTEM = """\
You are a hallucination detector for a travel concierge application.

You will receive:
1. **User query** — the customer's original question.
2. **Tool results** — the raw JSON data retrieved by the agent's tools
   (restaurants, flights, accommodations, experiences). This is the
   GROUND TRUTH.
3. **Agent response** — the text the concierge returned to the customer.

Your job is to check whether every factual claim in the agent response is
supported by the tool results.  Focus on:

- **Names**: restaurant, hotel, flight, experience names must appear in the
  tool results.
- **Prices**: dollar amounts must match (small rounding is OK).
- **Ratings**: star ratings must match.
- **IDs / Links**: any ``/restaurants?id=rest-xxx`` style links must reference
  IDs present in the tool results.
- **Descriptions**: paraphrasing is fine, but inventing features or specialties
  not in the data is a hallucination.
- **Flights**: airline, flight number, route, class, and price must match.

If the agent adds subjective commentary, travel tips, or asks follow-up
questions, that is NOT a hallucination — only verifiable facts matter.

If no tool results were provided (the agent answered from its instructions
without calling tools), score based on whether the response stays within the
agent's stated capabilities and doesn't fabricate specific data.

Return ONLY a JSON object (no markdown fences):
{
  "score": <float 0.0 to 1.0>,
  "hallucinated_claims": ["list of specific fabricated claims, if any"],
  "reasoning": "<brief explanation>"
}

Scoring guide:
- 1.0  = every factual claim is grounded in tool results
- 0.75 = minor inaccuracies (slight price rounding, truncated description)
- 0.5  = some claims lack support but core recommendations are real
- 0.25 = multiple fabricated items or significantly wrong data
- 0.0  = response is largely fabricated
"""


# ── Inline judge (called from main.py) ───────────────────────────────

async def hallucination_judge(
    user_message: str,
    agent_response: str,
    tool_context: list[str],
    workflow_span,
    agent_name: str = "concierge",
) -> float | None:
    """Run the LLM-as-judge and submit evaluation to Datadog LLMObs.

    Parameters
    ----------
    user_message : str
        The customer's original query.
    agent_response : str
        The full text the concierge returned.
    tool_context : list[str]
        Raw JSON strings from function_response parts captured during
        the agent turn.  Each entry is the serialised return value of
        one tool call.
    workflow_span
        The active ``LLMObs.workflow()`` span to attach the evaluation to.
    agent_name : str
        Label suffix for the Datadog evaluation metric.

    Returns
    -------
    float | None
        The hallucination score (0–1), or None if the judge call failed.
    """
    if not agent_response.strip():
        return None

    # Build the judge prompt
    tool_context_text = "\n---\n".join(tool_context) if tool_context else "(no tools were called)"
    judge_prompt = (
        f"## User query\n{user_message}\n\n"
        f"## Tool results (ground truth)\n{tool_context_text}\n\n"
        f"## Agent response\n{agent_response}"
    )

    try:
        client = genai.Client()
        response = await client.aio.models.generate_content(
            model=_JUDGE_MODEL,
            contents=judge_prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=_JUDGE_SYSTEM,
                temperature=0.0,
            ),
        )

        raw = response.text.strip()
        # Strip markdown fences if present
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        result = json.loads(raw)
        score = float(result["score"])
        hallucinated = result.get("hallucinated_claims", [])
        reasoning = result.get("reasoning", "")

        # Submit to Datadog LLMObs
        exported = LLMObs.export_span(span=workflow_span)
        if exported:
            LLMObs.submit_evaluation(
                span_context=exported,
                label=f"hallucination_score.{agent_name}",
                metric_type="score",
                value=score,
            )

        if hallucinated:
            logger.warning(
                "Hallucination detected (score=%.2f, agent=%s): %s — %s",
                score, agent_name, hallucinated, reasoning,
            )
        else:
            logger.info(
                "Hallucination check passed (score=%.2f, agent=%s): %s",
                score, agent_name, reasoning,
            )

        return score

    except Exception:
        logger.exception("Hallucination judge failed for agent=%s", agent_name)
        return None


# ── Experiment evaluator (sync, for ddtrace experiment framework) ────

def hallucination_score(input_data, output_data, expected_output):
    """LLM-as-judge evaluator compatible with ``LLMObs.experiment()``.

    ``input_data`` should contain:
      - ``query`` (str): the user message
      - ``tool_context`` (list[str], optional): raw tool results

    ``output_data`` is the agent's response string.
    """
    import asyncio

    query = input_data.get("query", "")
    tool_ctx = input_data.get("tool_context", [])

    if not output_data or not output_data.strip():
        return EvaluatorResult(
            value=0.0,
            reasoning="Empty agent response",
            assessment="fail",
            tags={"evaluator": "hallucination_score"},
        )

    tool_context_text = "\n---\n".join(tool_ctx) if tool_ctx else "(no tools were called)"
    judge_prompt = (
        f"## User query\n{query}\n\n"
        f"## Tool results (ground truth)\n{tool_context_text}\n\n"
        f"## Agent response\n{output_data}"
    )

    try:
        client = genai.Client()

        async def _call():
            resp = await client.aio.models.generate_content(
                model=_JUDGE_MODEL,
                contents=judge_prompt,
                config=genai.types.GenerateContentConfig(
                    system_instruction=_JUDGE_SYSTEM,
                    temperature=0.0,
                ),
            )
            return resp.text.strip()

        raw = asyncio.run(_call())
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        result = json.loads(raw)
        score = float(result["score"])
        hallucinated = result.get("hallucinated_claims", [])
        reasoning = result.get("reasoning", "")

        assessment = "pass" if score >= 0.75 else "fail"
        detail = reasoning
        if hallucinated:
            detail += f" | Hallucinated: {hallucinated}"

        return EvaluatorResult(
            value=score,
            reasoning=detail,
            assessment=assessment,
            tags={"evaluator": "hallucination_score"},
        )

    except Exception as exc:
        return EvaluatorResult(
            value=0.0,
            reasoning=f"Judge call failed: {exc}",
            assessment="error",
            tags={"evaluator": "hallucination_score"},
        )
