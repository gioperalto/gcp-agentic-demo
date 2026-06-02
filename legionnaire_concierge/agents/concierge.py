import os
from datetime import datetime

from google.adk.agents.llm_agent import Agent

from ..tools import (
    search_affordable_accommodations,
    search_affordable_restaurants,
    search_economy_flights,
    search_affordable_experiences,
)
from ..prompts import legionnaire_instruction

MODEL = os.getenv("GOOGLE_GENAI_MODEL", "gemini-2.0-flash")

legionnaire_agent = Agent(
    model=MODEL,
    name="Concierge",
    description="Budget-focused travel concierge for Legionnaire cardholders.",
    instruction=legionnaire_instruction(datetime.now().strftime("%A, %B %d, %Y")),
    tools=[
        search_affordable_accommodations,
        search_affordable_restaurants,
        search_economy_flights,
        search_affordable_experiences,
    ],
)
