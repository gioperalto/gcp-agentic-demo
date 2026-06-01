import os

from google.adk.agents.llm_agent import Agent
from google.adk.tools import FunctionTool

from ..tools.jenny import search_flights, compare_flight_prices, get_flight_details
from ._live_utils import _transfer_tool, _end_tool
from ..prompts import JENNY_INSTRUCTION, LIVE_JENNY_INSTRUCTION

MODEL = os.getenv("GOOGLE_GENAI_MODEL")
LIVE_MODEL = os.getenv("GOOGLE_GENAI_LIVE_MODEL", "gemini-live-2.5-flash-native-audio")

flight_agent = Agent(
    model=MODEL,
    name="Jenny",
    description="Agent specialized in searching premium flights for Tribune cardholders.",
    instruction=JENNY_INSTRUCTION,
    tools=[FunctionTool(search_flights), FunctionTool(compare_flight_prices), FunctionTool(get_flight_details)],
)

live_flight_agent = Agent(
    model=LIVE_MODEL,
    name="Jenny",
    description="Voice agent specialized in searching premium flights for Tribune cardholders.",
    instruction=LIVE_JENNY_INSTRUCTION,
    tools=[FunctionTool(search_flights), FunctionTool(compare_flight_prices), FunctionTool(get_flight_details), _transfer_tool, _end_tool],
)
