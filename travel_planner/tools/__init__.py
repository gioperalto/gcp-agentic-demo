"""
Travel Planner Agent Tools
This package contains domain-specific tools for each agent.
"""

from .jenny import search_flights, compare_flight_prices
from .marcus import search_accommodations, get_accommodation_reviews
from .sofia import search_attractions, create_daily_itinerary, check_operating_hours
from .luca import get_restaurant_recommendations
from .alex import calculate_trip_cost, check_budget_status, suggest_cost_savings, allocate_budget

__all__ = [
    # Jenny's tools
    'search_flights',
    'compare_flight_prices',
    # Marcus's tools
    'search_accommodations',
    'get_accommodation_reviews',
    # Sofia's tools
    'search_attractions',
    'create_daily_itinerary',
    'check_operating_hours',
    'get_restaurant_recommendations',
    # Alex's tools
    'calculate_trip_cost',
    'check_budget_status',
    'suggest_cost_savings',
    'allocate_budget',
]
