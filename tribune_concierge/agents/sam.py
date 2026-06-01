import os
from datetime import datetime

from google.adk.agents.llm_agent import Agent

from ._live_utils import _transfer_tool, _end_tool
from ..prompts import AGENT_VOICE_MAP, sam_instruction, live_sam_instruction
from .jenny import flight_agent, live_flight_agent
from .marcus import accommodation_agent, live_accommodation_agent
from .sofia import itinerary_agent, live_itinerary_agent
from .luca import restaurant_agent, live_restaurant_agent
from .ralph import utility_agent, live_utility_agent

MODEL = os.getenv("GOOGLE_GENAI_MODEL")
LIVE_MODEL = os.getenv("GOOGLE_GENAI_LIVE_MODEL", "gemini-live-2.5-flash-native-audio")

root_agent = Agent(
    model=MODEL,
    name="Sam",
    description="Premium travel concierge for Tribune cardholders coordinating luxury travel experiences.",
    instruction=sam_instruction(datetime.now().strftime("%A, %B %d, %Y")),
    sub_agents=[utility_agent, flight_agent, accommodation_agent, itinerary_agent, restaurant_agent],
)

live_root_agent = Agent(
    model=LIVE_MODEL,
    name="Sam",
    description="Voice-enabled premium travel concierge for Tribune cardholders.",
    instruction=live_sam_instruction(datetime.now().strftime("%A, %B %d, %Y")),
    tools=[_transfer_tool, _end_tool],
)

LIVE_AGENT_MAP = {
    "Sam": live_root_agent,
    "Jenny": live_flight_agent,
    "Marcus": live_accommodation_agent,
    "Sofia": live_itinerary_agent,
    "Luca": live_restaurant_agent,
    "Ralph": live_utility_agent,
}
