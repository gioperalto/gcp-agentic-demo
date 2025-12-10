"""
Sofia's Itinerary Tools
This module contains tool functions for itinerary building, attractions, and restaurant recommendations.
"""

from typing import Dict, List, Any
import random


def search_attractions(
    destination: str,
    interests: List[str] = None,
    date: str = None
) -> Dict[str, Any]:
    """
    Search for attractions and activities in a destination.

    Args:
        destination: City or location
        interests: List of interest categories (culture, food, adventure, relaxation)
        date: Specific date to check availability

    Returns:
        List of attractions with details
    """
    attraction_types = ['Museum', 'Park', 'Restaurant', 'Monument', 'Beach', 'Market', 'Gallery']
    attractions = []

    for i in range(6):
        attractions.append({
            'id': f'ATT{random.randint(1000, 9999)}',
            'name': f'{random.choice(["Historic", "Modern", "Famous", "Hidden"])} {random.choice(attraction_types)}',
            'type': random.choice(attraction_types),
            'destination': destination,
            'rating': round(random.uniform(4.0, 5.0), 1),
            'price': random.choice([0, 10, 15, 20, 25, 30]),
            'duration': f'{random.randint(1, 4)} hours',
            'opening_hours': '09:00 - 18:00',
            'best_time_to_visit': random.choice(['Morning', 'Afternoon', 'Evening']),
            'description': f'Popular {attraction_types[i % len(attraction_types)].lower()} in {destination}'
        })

    return {
        'status': 'success',
        'destination': destination,
        'attractions': attractions,
        'total_results': len(attractions)
    }


def create_daily_itinerary(
    destination: str,
    date: str,
    attractions: List[str],
    preferences: str = None
) -> Dict[str, Any]:
    """
    Create a detailed daily itinerary.

    Args:
        destination: City or location
        date: Date for the itinerary
        attractions: List of attraction IDs to include
        preferences: User preferences as JSON string (pace, meal times, etc.)

    Returns:
        Structured daily itinerary
    """
    schedule = []
    times = ['09:00', '11:00', '13:00', '15:00', '17:00', '19:00']

    for i, attraction_id in enumerate(attractions[:len(times)]):
        schedule.append({
            'time': times[i],
            'activity': f'Visit {attraction_id}',
            'duration': f'{random.randint(1, 3)} hours',
            'notes': 'Check for tickets in advance' if random.choice([True, False]) else ''
        })

    return {
        'status': 'success',
        'date': date,
        'destination': destination,
        'schedule': schedule,
        'total_activities': len(schedule),
        'estimated_cost': sum([random.randint(10, 50) for _ in schedule])
    }


def check_operating_hours(attraction_id: str, date: str) -> Dict[str, Any]:
    """
    Check operating hours for a specific attraction on a given date.

    Args:
        attraction_id: Attraction identifier
        date: Date to check (YYYY-MM-DD)

    Returns:
        Operating hours and availability
    """
    return {
        'status': 'success',
        'attraction_id': attraction_id,
        'date': date,
        'is_open': True,
        'hours': {
            'opening': '09:00',
            'closing': '18:00'
        },
        'special_notes': 'Last entry 30 minutes before closing'
    }


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
        List of restaurant recommendations
    """
    cuisines = ['Italian', 'Japanese', 'Mexican', 'French', 'American', 'Thai']
    restaurants = []

    price_map = {'low': '$', 'medium': '$$', 'high': '$$$'}

    for i in range(4):
        restaurants.append({
            'id': f'REST{random.randint(1000, 9999)}',
            'name': f"The {random.choice(['Golden', 'Silver', 'Happy', 'Tasty'])} {random.choice(cuisines)}",
            'cuisine': cuisine_type or random.choice(cuisines),
            'price_range': price_map.get(price_range, '$$'),
            'rating': round(random.uniform(4.0, 5.0), 1),
            'location': destination,
            'average_cost_per_person': random.randint(15, 60),
            'reservation_required': random.choice([True, False])
        })

    return {
        'status': 'success',
        'destination': destination,
        'meal_type': meal_type,
        'restaurants': restaurants
    }
