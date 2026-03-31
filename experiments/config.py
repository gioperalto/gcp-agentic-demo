"""
Shared configuration for Datadog LLM Observability Experiments.

Initialises LLMObs once and exposes helper constants used by every
specialist experiment module.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from the project root
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

# Ensure the backend package is importable so tool modules resolve
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ddtrace.llmobs import LLMObs

# ── Datadog credentials ──────────────────────────────────────────────
DD_API_KEY = os.getenv("DATADOG_API_KEY")
DD_APP_KEY = os.getenv("DD_APPLICATION_KEY") or os.getenv("DD_APP_KEY")
DD_SITE = os.getenv("DD_SITE", "datadoghq.com")

PROJECT_NAME = "Travel Planner"
ML_APP = "travel-planner"


def init_llmobs():
    """Initialise LLMObs for experiment usage (idempotent)."""
    LLMObs.enable(
        api_key=DD_API_KEY,
        app_key=DD_APP_KEY,
        site=DD_SITE,
        project_name=PROJECT_NAME,
        ml_app=ML_APP,
    )


# ── Countries available in the dataset ────────────────────────────────
COUNTRIES = ["Argentina", "Brazil", "Mexico", "Japan", "Spain", "Italy"]
