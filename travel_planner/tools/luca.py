"""
Luca's Restaurant Tools
This module contains tool functions for restaurant recommendations and dining reservations.
"""

from typing import Dict, List, Any, Optional
from .restaurants import normalize_cuisine_type


def get_restaurant_recommendations(
    destination: str,
    cuisine_type: str = None,
    price_range: str = 'medium',
    meal_type: str = 'dinner'
) -> Dict[str, Any]:
    """
    Get restaurant recommendations for a destination.

    Args:
        destination: City or location
        cuisine_type: Type of cuisine
        price_range: Budget level (low, medium, high)
        meal_type: Breakfast, lunch, or dinner

    Returns:
        Dictionary with search criteria to help the agent find real restaurant data online.
    """
    # Normalize the cuisine type to match predefined list if provided
    normalized_cuisine = normalize_cuisine_type(cuisine_type) if cuisine_type else None

    # Build search query
    search_guidance = f"Search for restaurants in {destination}"

    if normalized_cuisine:
        search_guidance += f" serving {normalized_cuisine} cuisine"

    search_guidance += f" suitable for {meal_type}"

    price_descriptors = {
        'low': 'budget-friendly ($ range)',
        'medium': 'mid-range ($$ range)',
        'high': 'upscale ($$$ range)'
    }
    search_guidance += f" in the {price_descriptors.get(price_range, 'medium')} price range"

    search_guidance += ". Search on platforms like Google Maps, Yelp, TripAdvisor, OpenTable, or The Fork for current information including ratings, reviews, menus, prices, and reservation availability."

    return {
        'status': 'search_required',
        'message': search_guidance,
        'search_criteria': {
            'destination': destination,
            'cuisine_type': normalized_cuisine,
            'price_range': price_range,
            'meal_type': meal_type
        },
        'suggested_sources': [
            'Google Maps',
            'Yelp',
            'TripAdvisor',
            'OpenTable',
            'The Fork',
            'Zomato',
            'Local food blogs'
        ],
        'information_to_gather': [
            'Restaurant name',
            'Cuisine type',
            'Price range',
            'Average cost per person',
            'User ratings and reviews',
            'Location and how to get there',
            'Opening hours',
            'Reservation requirements',
            'Popular dishes',
            'Dietary options available'
        ]
    }
