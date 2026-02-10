"""
Luca's Restaurant Tools
This module contains tool functions for restaurant recommendations and dining reservations.
"""

import json
import os
from typing import Dict, List, Any, Optional
from .restaurants import normalize_cuisine_type


def _load_restaurants_data() -> List[Dict[str, Any]]:
    """Load restaurants data from JSON file."""
    data_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'backend', 'data', 'restaurants.json'
    )
    try:
        with open(data_path, 'r') as f:
            data = json.load(f)
            return data.get('restaurants', [])
    except FileNotFoundError:
        return []


def get_restaurant_recommendations(
    destination: str,
    cuisine_type: str = None,
    price_range: str = 'high',
    meal_type: str = 'dinner',
    min_rating: float = 4.5
) -> Dict[str, Any]:
    """
    Get high-end restaurant recommendations for Tribune cardholders.
    Focuses on $$$ and $$$$ restaurants with exceptional ratings.

    Args:
        destination: City or location
        cuisine_type: Type of cuisine
        price_range: Budget level (low, medium, high) - defaults to 'high'
        meal_type: Breakfast, lunch, or dinner
        min_rating: Minimum rating (defaults to 4.5 for high-end)

    Returns:
        Dictionary with luxury restaurant options and clickable links.
    """
    # Load restaurants from local data
    all_restaurants = _load_restaurants_data()

    # Filter by destination (city or country)
    city_matches = [rest for rest in all_restaurants
                   if destination.lower() in rest.get('city', '').lower()
                   or destination.lower() in rest.get('country', '').lower()]

    # Focus on HIGH-END restaurants: $$$ and $$$$ price ranges
    luxury_restaurants = [
        rest for rest in city_matches
        if rest.get('affordabilityTier') in ['mid-range', 'luxury'] and
        rest.get('priceRange') in ['$$$', '$$$$'] and
        rest.get('rating', 0) >= min_rating
    ]

    # Apply optional filters
    filtered = luxury_restaurants

    if cuisine_type:
        cuisine_lower = cuisine_type.lower()
        filtered = [
            rest for rest in filtered
            if cuisine_lower in rest.get('cuisine', '').lower()
        ]

    # Map price_range parameter to priceRange in data
    if price_range == 'high':
        # Already filtered for $$$ and $$$$
        pass
    elif price_range == 'medium':
        filtered = [rest for rest in filtered if rest.get('priceRange') == '$$$']
    elif price_range == 'low':
        # For Tribune cardholders, still show mid-range at minimum
        filtered = [rest for rest in filtered if rest.get('priceRange') in ['$$', '$$$']]

    # Sort by rating and avg price (highest first)
    filtered.sort(key=lambda x: (x.get('rating', 0), x.get('avgPricePerPerson', 0)), reverse=True)

    # Build response with clickable links
    if not filtered:
        return {
            'status': 'no_results',
            'message': f'No high-end restaurants found in {destination} matching your criteria. Consider broadening your search.',
            'filters_applied': {
                'destination': destination,
                'cuisine_type': cuisine_type,
                'price_range': price_range,
                'min_rating': min_rating
            }
        }

    # Format results with links
    results_text = f"I found **{len(filtered)} exceptional dining experiences** in {destination}:\n\n"

    for rest in filtered[:10]:  # Show top 10
        rest_id = rest.get('id')
        name = rest.get('name')
        cuisine = rest.get('cuisine', 'International')
        rating = rest.get('rating', 'N/A')
        price_range_symbol = rest.get('priceRange', '')
        avg_price = rest.get('avgPricePerPerson', 'N/A')
        description = rest.get('description', '')

        results_text += f"**[{name}](/restaurants?id={rest_id})**\n"
        results_text += f"- Cuisine: {cuisine} | Rating: {rating}★ | {price_range_symbol} (${avg_price}/person)\n"
        results_text += f"- {description[:120]}{'...' if len(description) > 120 else ''}\n\n"

    return {
        'status': 'success',
        'message': results_text,
        'restaurants': filtered[:10],
        'total_found': len(filtered)
    }


def get_restaurant_details(restaurant_id: str) -> Dict[str, Any]:
    """
    Get detailed information for a specific restaurant.

    Args:
        restaurant_id: Unique identifier for the restaurant

    Returns:
        Detailed restaurant information with link
    """
    # Load restaurants from local data
    all_restaurants = _load_restaurants_data()

    # Find the specific restaurant
    restaurant = next((rest for rest in all_restaurants if rest.get('id') == restaurant_id), None)

    if not restaurant:
        return {
            'status': 'not_found',
            'message': f'Restaurant with ID {restaurant_id} not found.',
            'restaurant_id': restaurant_id
        }

    # Build detailed response
    name = restaurant.get('name')
    cuisine = restaurant.get('cuisine', 'International')
    rating = restaurant.get('rating', 'N/A')
    price_range = restaurant.get('priceRange', '')
    avg_price = restaurant.get('avgPricePerPerson', 'N/A')
    city = restaurant.get('city', '')
    country = restaurant.get('country', '')
    address = restaurant.get('address', '')
    description = restaurant.get('description', '')
    specialties = restaurant.get('specialties', [])
    reservation_available = restaurant.get('reservationAvailable', False)

    details_text = f"**[{name}](/restaurants?id={restaurant_id})**\n\n"
    details_text += f"**Location:** {city}, {country}\n"
    details_text += f"**Address:** {address}\n"
    details_text += f"**Cuisine:** {cuisine} | **Rating:** {rating}★\n"
    details_text += f"**Price:** {price_range} (${avg_price} per person)\n"
    details_text += f"**Reservations:** {'Available' if reservation_available else 'Walk-in only'}\n\n"
    details_text += f"**About:** {description}\n\n"

    if specialties:
        details_text += f"**Specialties:**\n"
        for specialty in specialties:
            details_text += f"- {specialty}\n"

    details_text += f"\n[Make a Reservation](/restaurants?id={restaurant_id})"

    return {
        'status': 'success',
        'message': details_text,
        'restaurant': restaurant
    }
