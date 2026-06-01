import os

from google.adk.agents.llm_agent import Agent
from google.adk.tools import FunctionTool

from ..tools.marcus import search_accommodations, get_accommodation_reviews
from ._live_utils import _transfer_tool, _end_tool
from ..prompts import MARCUS_INSTRUCTION, LIVE_MARCUS_INSTRUCTION

MODEL = os.getenv("GOOGLE_GENAI_MODEL")
LIVE_MODEL = os.getenv("GOOGLE_GENAI_LIVE_MODEL", "gemini-live-2.5-flash-native-audio")

accommodation_agent = Agent(
    model=MODEL,
    name="Marcus",
    description="Agent specialized in luxury accommodations for Tribune cardholders.",
    instruction=MARCUS_INSTRUCTION,
    tools=[FunctionTool(search_accommodations), FunctionTool(get_accommodation_reviews)],
)

live_accommodation_agent = Agent(
    model=LIVE_MODEL,
    name="Marcus",
    description="Voice agent specialized in luxury accommodations for Tribune cardholders.",
    instruction=LIVE_MARCUS_INSTRUCTION,
    tools=[FunctionTool(search_accommodations), FunctionTool(get_accommodation_reviews), _transfer_tool, _end_tool],
)
