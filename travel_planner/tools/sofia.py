"""
Sofia's Itinerary Tools
This module contains tool functions for itinerary building, attractions, and restaurant recommendations.
"""

from typing import Dict, List, Any, Optional


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
        Dictionary with search criteria to help the agent find real attraction data online.
    """
    # Build search query
    search_guidance = f"Search for attractions and things to do in {destination}"

    if interests:
        search_guidance += f" focusing on interests like: {', '.join(interests)}"

    if date:
        search_guidance += f" available on {date}"

    search_guidance += ". Look for popular tourist attractions, museums, parks, monuments, beaches, markets, galleries, and activities. Check TripAdvisor, Google Maps, local tourism websites, and travel guides for current information including ratings, opening hours, ticket prices, and visitor reviews."

    return {
        'status': 'search_required',
        'message': search_guidance,
        'search_criteria': {
            'destination': destination,
            'interests': interests,
            'date': date
        },
        'suggested_sources': [
            'TripAdvisor',
            'Google Maps/Travel',
            'Viator',
            'GetYourGuide',
            'Local tourism board websites',
            'Lonely Planet',
            'Time Out'
        ],
        'information_to_gather': [
            'Attraction name and type',
            'Location and how to get there',
            'Opening hours',
            'Ticket prices',
            'Average visit duration',
            'Best time to visit',
            'User ratings and reviews',
            'Booking requirements'
        ]
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
        Guidance for creating an itinerary
    """
    search_guidance = f"Create a detailed itinerary for {destination} on {date}"

    if attractions:
        search_guidance += f" including these attractions: {', '.join(attractions)}"

    if preferences:
        search_guidance += f" considering preferences: {preferences}"

    search_guidance += ". Research each attraction's opening hours, typical visit duration, and location. Organize them logically based on proximity to minimize travel time. Include buffer time between activities, meal breaks, and rest periods. Consider the best visiting times for each attraction (e.g., museums in the morning, sunset viewpoints in the evening)."

    return {
        'status': 'search_required',
        'message': search_guidance,
        'itinerary_planning_criteria': {
            'destination': destination,
            'date': date,
            'attractions': attractions,
            'preferences': preferences
        },
        'planning_considerations': [
            'Opening and closing hours of each attraction',
            'Estimated time needed at each location',
            'Travel time between locations',
            'Meal times and restaurant locations',
            'Peak visiting times and crowds',
            'Energy levels throughout the day',
            'Weather conditions',
            'Booking requirements'
        ]
    }


def check_operating_hours(attraction_id: str, date: str) -> Dict[str, Any]:
    """
    Check operating hours for a specific attraction on a given date.

    Args:
        attraction_id: Attraction identifier
        date: Date to check (YYYY-MM-DD)

    Returns:
        Guidance for checking operating hours
    """
    return {
        'status': 'search_required',
        'message': f'To check the operating hours for {attraction_id} on {date}, search for the attraction\'s official website or check platforms like Google Maps, TripAdvisor, or the venue\'s social media. Look for: regular operating hours, special holiday hours, last entry times, days when it\'s closed, and any seasonal variations. Also check if advance booking is required.',
        'attraction_id': attraction_id,
        'date': date,
        'information_to_check': [
            'Regular operating hours',
            'Special hours for the specific date',
            'Days closed (if any)',
            'Last entry/admission time',
            'Seasonal variations',
            'Holiday closures',
            'Advance booking requirements',
            'Peak times to avoid crowds'
        ]
    }
