"""
Feature Flag Service
Lightweight service that reads/writes flag state from a local JSON file
and tags the active ddtrace span with flag evaluation results.
"""

import json
from pathlib import Path
from ddtrace import tracer

FLAGS_PATH = Path(__file__).parent.parent / "data" / "feature_flags.json"


def _load_flags() -> dict:
    """Load the feature flags JSON file."""
    if not FLAGS_PATH.exists():
        return {}
    with open(FLAGS_PATH, "r") as f:
        return json.load(f)


def _save_flags(flags: dict) -> None:
    """Persist the feature flags dict back to the JSON file."""
    with open(FLAGS_PATH, "w") as f:
        json.dump(flags, f, indent=2)


def evaluate_flag(flag_name: str, default: bool = False) -> bool:
    """
    Evaluate a feature flag by name.

    Reads the JSON store, resolves the flag value (falling back to `default`),
    and tags the active ddtrace span so the evaluation is visible in APM.

    Args:
        flag_name: The flag identifier (e.g. "insecure-profile-agent")
        default: Value to return if the flag is not found

    Returns:
        bool: The resolved flag value
    """
    flags = _load_flags()
    flag_data = flags.get(flag_name)

    if flag_data is None:
        value = default
    else:
        value = flag_data.get("enabled", default)

    # Tag the active ddtrace span with the flag evaluation
    span = tracer.current_span()
    if span:
        span.set_tag(f"feature_flag.{flag_name}.variant", str(value).lower())
        span.set_tag("feature_flag.provider", "local")

    return value


def set_flag(flag_name: str, enabled: bool) -> dict:
    """
    Update a feature flag's enabled state.

    Args:
        flag_name: The flag identifier
        enabled: The new enabled state

    Returns:
        dict: The updated flag entry (with flag_name, enabled, description)
    """
    flags = _load_flags()

    if flag_name not in flags:
        flags[flag_name] = {"enabled": enabled, "description": ""}
    else:
        flags[flag_name]["enabled"] = enabled

    _save_flags(flags)

    return {
        "flag_name": flag_name,
        "enabled": flags[flag_name]["enabled"],
        "description": flags[flag_name].get("description", ""),
    }


def get_all_flags() -> dict:
    """
    Return the entire feature flags dictionary.

    Returns:
        dict: All flags with their current state and descriptions
    """
    return _load_flags()
