import os
from dotenv import load_dotenv
from ddtrace.llmobs import LLMObs
from google.adk.agents.llm_agent import Agent
from google.adk.tools import FunctionTool
from .tools.jenny import search_flights, compare_flight_prices
from .tools.marcus import search_accommodations, get_accommodation_reviews
from .tools.sofia import search_attractions, create_daily_itinerary, check_operating_hours, get_restaurant_recommendations
from .tools.alex import calculate_trip_cost, check_budget_status, suggest_cost_savings, allocate_budget

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
    name='Jenny',
    description='Agent specialized in searching and booking flights.',
    instruction='''You are Jenny, the Flight Search Agent. Your responsibilities include searching for flights based on user preferences
, comparing prices, and assisting with booking. Use available tools to access flight databases and provide users with the best options.
Always introduce yourself as Jenny when you first interact with a user.''',
    tools=[FunctionTool(search_flights), FunctionTool(compare_flight_prices)],
)

# Accommodation sub-agent
accomadation_agent = Agent(
    model=os.getenv("GOOGLE_GENAI_MODEL"),
    name='Marcus',
    description='Agent specialized in searching and booking accommodations.',
    instruction='''You are Marcus, the Accommodation Agent. Your responsibilities include searching for accommodations based on user preferences
, comparing prices, and assisting with booking. Use available tools to access accommodation databases and provide users with the best options.
Always introduce yourself as Marcus when you first interact with a user.''',
    tools=[FunctionTool(search_accommodations), FunctionTool(get_accommodation_reviews)],
)

# Itinerary sub-agent
itinerary_agent = Agent(
    model=os.getenv("GOOGLE_GENAI_MODEL"),
    name='Sofia',
    description='Agent specialized in creating travel itineraries.',
    instruction='''You are Sofia, the Itinerary Agent. Your responsibilities include creating detailed travel itineraries
based on user preferences, including activities, dining options, and sightseeing. Use available tools to gather information and provide users with comprehensive itineraries.
Always introduce yourself as Sofia when you first interact with a user.''',
    tools=[FunctionTool(search_attractions), FunctionTool(create_daily_itinerary), FunctionTool(check_operating_hours), FunctionTool(get_restaurant_recommendations)],
)

# Budget management sub-agent
budget_manager_agent = Agent(
    model=os.getenv("GOOGLE_GENAI_MODEL"),
    name='Alex',
    description='Agent specialized in managing travel budgets.',
    instruction='''You are Alex, the Budget Manager Agent. Your responsibilities include helping users manage their travel budgets
by providing cost estimates, tracking expenses, and suggesting cost-saving options. Use available tools to gather pricing information and assist users in staying within their budgets.
Always introduce yourself as Alex when you first interact with a user.''',
    tools=[FunctionTool(calculate_trip_cost), FunctionTool(check_budget_status), FunctionTool(suggest_cost_savings), FunctionTool(allocate_budget)],
)

# Main agent
root_agent = Agent(
    model=os.getenv("GOOGLE_GENAI_MODEL"),
    name='Sam',
    description='A helpful travel planning assistant that coordinates with specialized agents.',
    instruction='''You are Sam, the main Travel Planner assistant. Your role is to understand user needs and coordinate with specialized agents:
- Jenny for flight searches and bookings
- Marcus for accommodation searches and bookings
- Sofia for itinerary planning and activities
- Alex for budget management
Greet users warmly and help them plan their perfect trip by directing them to the right specialist when needed.''',
    sub_agents=[flight_search_agent, accomadation_agent, itinerary_agent, budget_manager_agent],
    tools=[],
)
