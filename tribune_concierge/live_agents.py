import os
from datetime import datetime
from google.adk.agents.llm_agent import Agent
from google.adk.tools import FunctionTool

from .prompts import (
    AGENT_VOICE_MAP,
    LIVE_JENNY_INSTRUCTION,
    LIVE_MARCUS_INSTRUCTION,
    LIVE_SOFIA_INSTRUCTION,
    LIVE_LUCA_INSTRUCTION,
    LIVE_RALPH_INSTRUCTION,
    live_sam_instruction,
)
from .tools.jenny import search_flights, compare_flight_prices, get_flight_details
from .tools.marcus import search_accommodations, get_accommodation_reviews
from .tools.sofia import search_attractions, create_daily_itinerary, check_operating_hours
from .tools.luca import get_restaurant_recommendations, get_restaurant_details
from .tools.ralph import audit_all_travel_options, cross_reference_availability, compile_travel_brief

LIVE_MODEL = os.getenv("GOOGLE_GENAI_LIVE_MODEL", "gemini-live-2.5-flash-native-audio")


def transfer_to(agent_name: str) -> str:
    """Transfer the conversation to another agent. Only call this AFTER the user explicitly confirms they want to be transferred."""
    return f"Transfer to {agent_name} initiated. Say a brief goodbye."


def end_conversation() -> str:
    """Call this when the conversation is complete and the customer has been fully served."""
    return "Conversation ended."


_transfer_tool = FunctionTool(transfer_to)
_end_tool = FunctionTool(end_conversation)


live_flight_agent = Agent(
    model=LIVE_MODEL,
    name="Jenny",
    description="Voice agent specialized in searching premium flights for Tribune cardholders.",
    instruction=LIVE_JENNY_INSTRUCTION,
    tools=[FunctionTool(search_flights), FunctionTool(compare_flight_prices), FunctionTool(get_flight_details), _transfer_tool, _end_tool],
)

live_accommodation_agent = Agent(
    model=LIVE_MODEL,
    name="Marcus",
    description="Voice agent specialized in luxury accommodations for Tribune cardholders.",
    instruction=LIVE_MARCUS_INSTRUCTION,
    tools=[FunctionTool(search_accommodations), FunctionTool(get_accommodation_reviews), _transfer_tool, _end_tool],
)

live_itinerary_agent = Agent(
    model=LIVE_MODEL,
    name="Sofia",
    description="Voice agent specialized in premium experiences and luxury itineraries for Tribune cardholders.",
    instruction=LIVE_SOFIA_INSTRUCTION,
    tools=[FunctionTool(search_attractions), FunctionTool(create_daily_itinerary), FunctionTool(check_operating_hours), _transfer_tool, _end_tool],
)

live_restaurant_agent = Agent(
    model=LIVE_MODEL,
    name="Luca",
    description="Voice agent specialized in high-end dining experiences for Tribune cardholders.",
    instruction=LIVE_LUCA_INSTRUCTION,
    tools=[FunctionTool(get_restaurant_recommendations), FunctionTool(get_restaurant_details), _transfer_tool, _end_tool],
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

live_root_agent = Agent(
    model=LIVE_MODEL,
    name="Sam",
    description="Voice-enabled premium travel concierge for Tribune cardholders.",
    instruction=live_sam_instruction(datetime.now().strftime("%A, %B %d, %Y")),
    tools=[_transfer_tool, _end_tool],
)

LIVE_AGENT_MAP = {
    "Sam":   live_root_agent,
    "Jenny": live_flight_agent,
    "Marcus":live_accommodation_agent,
    "Sofia": live_itinerary_agent,
    "Luca":  live_restaurant_agent,
    "Ralph": live_utility_agent,
}
