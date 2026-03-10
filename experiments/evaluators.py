"""
Shared evaluators for all specialist experiments.

Each evaluator receives (input_data, output_data, expected_output) and returns
a bool, float, or EvaluatorResult.
"""

import re
from ddtrace.llmobs._experiment import EvaluationResult as EvaluatorResult


# ── Structural evaluators ─────────────────────────────────────────────

def contains_links(input_data, output_data, expected_output):
    """Check that the response includes at least one markdown link to
    the internal platform (e.g. /flights?id=..., /restaurants?id=...)."""
    pattern = r"\[.+?\]\(/(?:flights|accommodations|restaurants|experiences)\?id=[a-z0-9\-]+\)"
    matches = re.findall(pattern, output_data)
    return EvaluatorResult(
        value=len(matches) > 0,
        reasoning=f"Found {len(matches)} internal link(s)" if matches else "No internal links found",
        assessment="pass" if matches else "fail",
        tags={"evaluator": "contains_links"},
    )


def link_count(input_data, output_data, expected_output):
    """Return the number of internal platform links in the response."""
    pattern = r"\[.+?\]\(/(?:flights|accommodations|restaurants|experiences)\?id=[a-z0-9\-]+\)"
    return float(len(re.findall(pattern, output_data)))


def mentions_destination(input_data, output_data, expected_output):
    """Verify the response references the destination from the query."""
    destination = input_data.get("destination", "")
    if not destination:
        return True
    found = destination.lower() in output_data.lower()
    return EvaluatorResult(
        value=found,
        reasoning=f"Destination '{destination}' {'found' if found else 'not found'} in response",
        assessment="pass" if found else "fail",
        tags={"evaluator": "mentions_destination"},
    )


def response_not_empty(input_data, output_data, expected_output):
    """Ensure the agent actually produced a response."""
    return len(output_data.strip()) > 0


def no_external_booking_sites(input_data, output_data, expected_output):
    """Verify the response doesn't mention external booking platforms."""
    external_sites = [
        "booking.com", "expedia", "hotels.com", "kayak", "skyscanner",
        "tripadvisor", "airbnb.com", "opentable", "resy.com",
    ]
    lower_output = output_data.lower()
    violations = [site for site in external_sites if site in lower_output]
    return EvaluatorResult(
        value=len(violations) == 0,
        reasoning=f"No external sites mentioned" if not violations else f"External sites found: {violations}",
        assessment="pass" if not violations else "fail",
        tags={"evaluator": "no_external_booking_sites"},
    )


# ── Quality evaluators ────────────────────────────────────────────────

def premium_focus(input_data, output_data, expected_output):
    """Check that the response favours premium/luxury options."""
    premium_terms = [
        "luxury", "premium", "first class", "business class",
        "5-star", "five-star", "exclusive", "exceptional",
        "villa", "$$$$", "$$$", "michelin",
    ]
    lower_output = output_data.lower()
    hits = [t for t in premium_terms if t in lower_output]
    score = min(len(hits) / 3.0, 1.0)  # 3+ premium terms → 1.0
    return EvaluatorResult(
        value=score,
        reasoning=f"Premium terms found: {hits}" if hits else "No premium terms found",
        assessment="pass" if score >= 0.33 else "fail",
        tags={"evaluator": "premium_focus"},
    )


def introduces_self(input_data, output_data, expected_output):
    """Check that the specialist introduces themselves by name."""
    expected_name = expected_output.get("agent_name", "")
    if not expected_name:
        return True
    found = expected_name.lower() in output_data.lower()
    return EvaluatorResult(
        value=found,
        reasoning=f"Agent name '{expected_name}' {'found' if found else 'not found'} in response",
        assessment="pass" if found else "fail",
        tags={"evaluator": "introduces_self"},
    )


# ── Summary evaluators ────────────────────────────────────────────────

def avg_link_count(inputs, outputs, expected_outputs, evaluators_results):
    """Average number of internal links across all records."""
    counts = evaluators_results.get("link_count", [])
    if not counts:
        return 0.0
    return sum(counts) / len(counts)


def pass_rate_links(inputs, outputs, expected_outputs, evaluators_results):
    """Percentage of records that contained at least one internal link."""
    results = evaluators_results.get("contains_links", [])
    if not results:
        return 0.0
    passing = sum(1 for r in results if (r is True or (hasattr(r, 'value') and r.value)))
    return passing / len(results)
