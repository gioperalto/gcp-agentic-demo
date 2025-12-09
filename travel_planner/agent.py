import os
from dotenv import load_dotenv
from ddtrace.llmobs import LLMObs
from google.adk.agents.llm_agent import Agent
from google.adk.tools import FunctionTool
from .tools import *

# Load environment variables from .env file
load_dotenv()

LLMObs.enable(
  ml_app="travel-planner",
  api_key=os.getenv("DATADOG_API_KEY"),
  site="datadoghq.com",
  agentless_enabled=True,
)

# Flight search sub-agent
flight_search_agent = Agent(
    model=os.getenv("GOOGLE_GENAI_MODEL"),
    name='flight_search_agent',
    description='Agent specialized in searching and booking flights.',
    instruction='''You are the Flight Search Agent. Your responsibilities include searching for flights based on user preferences
, comparing prices, and assisting with booking. Use available tools to access flight databases and provide users with the best options.''',
    tools=[FunctionTool(search_flights), FunctionTool(compare_flight_prices)],
)

# Accommodation sub-agent
accomadation_agent = Agent(
    model=os.getenv("GOOGLE_GENAI_MODEL"),
    name='accomadation_agent',
    description='Agent specialized in searching and booking accommodations.',
    instruction='''You are the Accommodation Agent. Your responsibilities include searching for accommodations based on user preferences
, comparing prices, and assisting with booking. Use available tools to access accommodation databases and provide users with the best options.''',
    tools=[FunctionTool(search_accommodations), FunctionTool(get_accommodation_reviews)],
)

# Itinerary sub-agent
itinerary_agent = Agent(
    model=os.getenv("GOOGLE_GENAI_MODEL"),
    name='itinerary_agent',
    description='Agent specialized in creating travel itineraries.',
    instruction='''You are the Itinerary Agent. Your responsibilities include creating detailed travel itineraries
based on user preferences, including activities, dining options, and sightseeing. Use available tools to gather information and provide users with comprehensive itineraries.''',
    tools=[FunctionTool(search_attractions), FunctionTool(create_daily_itinerary), FunctionTool(check_operating_hours), FunctionTool(get_restaurant_recommendations)],
)

# Budget management sub-agent
budget_manager_agent = Agent(
    model=os.getenv("GOOGLE_GENAI_MODEL"),
    name='budget_manager_agent',
    description='Agent specialized in managing travel budgets.',
    instruction='''You are the Budget Manager Agent. Your responsibilities include helping users manage their travel budgets
by providing cost estimates, tracking expenses, and suggesting cost-saving options. Use available tools to gather pricing information and assist users in staying within their budgets.''',
    tools=[FunctionTool(calculate_trip_cost), FunctionTool(check_budget_status), FunctionTool(suggest_cost_savings), FunctionTool(allocate_budget)],
)

# Main agent
root_agent = Agent(
    model=os.getenv("GOOGLE_GENAI_MODEL"),
    name='travel_planner',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
    sub_agents=[flight_search_agent, accomadation_agent, itinerary_agent, budget_manager_agent],
    tools=[],
)
