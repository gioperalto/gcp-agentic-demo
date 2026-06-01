"""
Travel Planner Agent Tools
This package contains domain-specific tools for each agent.
"""

from .jenny import search_flights, compare_flight_prices, get_flight_details
from .marcus import search_accommodations, get_accommodation_reviews
from .sofia import search_attractions, create_daily_itinerary, check_operating_hours
from .luca import get_restaurant_recommendations, get_restaurant_details
from .ralph import audit_all_travel_options, cross_reference_availability, compile_travel_brief

__all__ = [
    # Jenny's tools
    'search_flights',
    'compare_flight_prices',
    'get_flight_details',
    # Marcus's tools
    'search_accommodations',
    'get_accommodation_reviews',
    # Sofia's tools
    'search_attractions',
    'create_daily_itinerary',
    'check_operating_hours',
    # Luca's tools
    'get_restaurant_recommendations',
    'get_restaurant_details',
    # Ralph's tools
    'audit_all_travel_options',
    'cross_reference_availability',
    'compile_travel_brief',
]
