import os

from google.adk.agents.llm_agent import Agent
from google.adk.tools import FunctionTool

from ..tools.luca import get_restaurant_recommendations, get_restaurant_details
from ._live_utils import _transfer_tool, _end_tool
from ..prompts import LUCA_INSTRUCTION, LIVE_LUCA_INSTRUCTION

MODEL = os.getenv("GOOGLE_GENAI_MODEL")
LIVE_MODEL = os.getenv("GOOGLE_GENAI_LIVE_MODEL", "gemini-live-2.5-flash-native-audio")

restaurant_agent = Agent(
    model=MODEL,
    name="Luca",
    description="Agent specialized in high-end dining experiences for Tribune cardholders.",
    instruction=LUCA_INSTRUCTION,
    tools=[FunctionTool(get_restaurant_recommendations), FunctionTool(get_restaurant_details)],
)

live_restaurant_agent = Agent(
    model=LIVE_MODEL,
    name="Luca",
    description="Voice agent specialized in high-end dining experiences for Tribune cardholders.",
    instruction=LIVE_LUCA_INSTRUCTION,
    tools=[FunctionTool(get_restaurant_recommendations), FunctionTool(get_restaurant_details), _transfer_tool, _end_tool],
)
