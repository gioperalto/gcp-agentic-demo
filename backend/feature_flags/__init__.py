"""
Registry of all Datadog feature flags used in this application.

FLAGS maps each flag key (as defined in Datadog Feature Management) to its
default (fallback) value used when the flag is unavailable.

Add new flags here — one entry per flag.
"""

INSECURE_PROFILE_AGENT = "insecure_profile_agent"
RALPH_AGENT = "ralph_agent"

FLAGS: dict[str, bool] = {
    INSECURE_PROFILE_AGENT: False,
    RALPH_AGENT: False,
}
