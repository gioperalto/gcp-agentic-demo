import os

from google.adk.agents.llm_agent import Agent
from google.adk.tools import FunctionTool

from ..tools.sofia import search_attractions, create_daily_itinerary, check_operating_hours
from ._live_utils import _transfer_tool, _end_tool
from ..prompts import SOFIA_INSTRUCTION, LIVE_SOFIA_INSTRUCTION

MODEL = os.getenv("GOOGLE_GENAI_MODEL")
LIVE_MODEL = os.getenv("GOOGLE_GENAI_LIVE_MODEL", "gemini-live-2.5-flash-native-audio")

itinerary_agent = Agent(
    model=MODEL,
    name="Sofia",
    description="Agent specialized in premium experiences and luxury itineraries for Tribune cardholders.",
    instruction=SOFIA_INSTRUCTION,
    tools=[FunctionTool(search_attractions), FunctionTool(create_daily_itinerary), FunctionTool(check_operating_hours)],
)

live_itinerary_agent = Agent(
    model=LIVE_MODEL,
    name="Sofia",
    description="Voice agent specialized in premium experiences and luxury itineraries for Tribune cardholders.",
    instruction=LIVE_SOFIA_INSTRUCTION,
    tools=[FunctionTool(search_attractions), FunctionTool(create_daily_itinerary), FunctionTool(check_operating_hours), _transfer_tool, _end_tool],
)
