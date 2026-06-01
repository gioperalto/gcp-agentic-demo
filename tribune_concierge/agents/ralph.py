import os

from google.adk.agents.llm_agent import Agent
from google.adk.tools import FunctionTool

from ..tools.ralph import audit_all_travel_options, cross_reference_availability, compile_travel_brief
from ._live_utils import _transfer_tool, _end_tool
from ..prompts import RALPH_INSTRUCTION, LIVE_RALPH_INSTRUCTION

MODEL = os.getenv("GOOGLE_GENAI_MODEL")
LIVE_MODEL = os.getenv("GOOGLE_GENAI_LIVE_MODEL", "gemini-live-2.5-flash-native-audio")

utility_agent = Agent(
    model=MODEL,
    name="Ralph",
    description="Utility travel coordinator handling broad travel planning and availability across all categories.",
    instruction=RALPH_INSTRUCTION,
    tools=[FunctionTool(audit_all_travel_options), FunctionTool(cross_reference_availability), FunctionTool(compile_travel_brief)],
)

live_utility_agent = Agent(
    model=LIVE_MODEL,
    name="Ralph",
    description="Voice utility coordinator handling broad travel planning and availability across all categories.",
    instruction=LIVE_RALPH_INSTRUCTION,
    tools=[
        FunctionTool(audit_all_travel_options),
        FunctionTool(cross_reference_availability),
        FunctionTool(compile_travel_brief),
        _transfer_tool,
        _end_tool,
    ],
)
