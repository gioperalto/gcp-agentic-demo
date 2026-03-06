"""
Sofia's Itinerary Tools
This module contains tool functions for itinerary building and experiences.
"""

from typing import Dict, List, Any, Optional

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
from services.travel_service import get_all_experiences, get_experience_by_id


def search_attractions(
    destination: str,
    interests: List[str] = None,
    date: str = None,
    min_rating: float = 4.5
) -> Dict[str, Any]:
    """
    Search for premium experiences and attractions for Tribune cardholders.
    Focuses on mid-range to luxury experiences.

    Args:
        destination: City or location
        interests: List of interest categories (hiking, atv, winery-tour, yacht, boat-tour, farm-to-table, adventure, cultural)
        date: Specific date to check availability
        min_rating: Minimum rating (defaults to 4.5 for quality)

    Returns:
        Dictionary with premium experience options and clickable links.
    """
    # Fetch experiences from the travel service layer
    try:
        experience_models = get_all_experiences()
        all_experiences = [e.model_dump() for e in experience_models]
    except Exception:
        return {
            'status': 'error',
            'message': 'Unable to retrieve experience data. Please try again later.'
        }

    # Client-side filter: destination (city or country)
    city_matches = [exp for exp in all_experiences
                   if destination.lower() in exp.get('city', '').lower()
                   or destination.lower() in exp.get('country', '').lower()]

    # Focus on MID-RANGE to LUXURY experiences
    premium_experiences = [
        exp for exp in city_matches
        if exp.get('affordabilityTier') in ['mid-range', 'luxury'] and
        exp.get('rating', 0) >= min_rating
    ]

    # Apply optional filters
    filtered = premium_experiences

    if interests:
        # Filter by experience type matching interests
        filtered = [
            exp for exp in filtered
            if any(interest.lower() in exp.get('type', '').lower() for interest in interests)
        ]

    # Sort by rating and price (highest first)
    filtered.sort(key=lambda x: (x.get('rating', 0), x.get('price', 0)), reverse=True)

    # Build response with clickable links
    if not filtered:
        return {
            'status': 'no_results',
            'message': f'No premium experiences found in {destination} matching your criteria. Consider broadening your search.',
            'filters_applied': {
                'destination': destination,
                'interests': interests,
                'min_rating': min_rating
            }
        }

    # Format results with links
    results_text = f"I found **{len(filtered)} exceptional experiences** in {destination}:\n\n"

    for exp in filtered[:10]:  # Show top 10
        exp_id = exp.get('id')
        name = exp.get('name')
        exp_type = exp.get('type', 'experience').replace('-', ' ').title()
        rating = exp.get('rating', 'N/A')
        price = exp.get('price', 'N/A')
        duration = exp.get('duration', 'N/A')
        description = exp.get('description', '')

        results_text += f"**[{name}](/experiences?id={exp_id})**\n"
        results_text += f"- Type: {exp_type} | Rating: {rating}★ | ${price} | Duration: {duration}\n"
        results_text += f"- {description[:120]}{'...' if len(description) > 120 else ''}\n\n"

    return {
        'status': 'success',
        'message': results_text,
        'experiences': filtered[:10],
        'total_found': len(filtered)
    }


def create_daily_itinerary(
    destination: str,
    date: str,
    experience_ids: List[str] = None,
    preferences: str = None
) -> Dict[str, Any]:
    """
    Create a detailed daily itinerary with luxury experiences.

    Args:
        destination: City or location
        date: Date for the itinerary
        experience_ids: List of experience IDs to include
        preferences: User preferences (pace, interests, etc.)

    Returns:
        Detailed itinerary with links to experiences
    """
    try:
        if experience_ids:
            # Fetch each experience by ID from the travel service layer
            selected_experiences = []
            for eid in experience_ids:
                exp_model = get_experience_by_id(eid)
                if exp_model is not None:
                    selected_experiences.append(exp_model.model_dump())
        else:
            # Fetch all experiences and filter by destination
            experience_models = get_all_experiences()
            all_experiences = [e.model_dump() for e in experience_models]
            city_matches = [exp for exp in all_experiences
                           if destination.lower() in exp.get('city', '').lower()
                           or destination.lower() in exp.get('country', '').lower()]
            premium_experiences = [
                exp for exp in city_matches
                if exp.get('affordabilityTier') in ['mid-range', 'luxury']
            ]
            # Sort by rating
            premium_experiences.sort(key=lambda x: x.get('rating', 0), reverse=True)
            selected_experiences = premium_experiences[:3]  # Top 3
    except Exception:
        return {
            'status': 'error',
            'message': 'Unable to retrieve experience data. Please try again later.'
        }

    if not selected_experiences:
        return {
            'status': 'no_results',
            'message': f'No experiences found to create an itinerary for {destination} on {date}.'
        }

    # Build itinerary
    itinerary_text = f"**Luxury Itinerary for {destination}** - {date}\n\n"

    for i, exp in enumerate(selected_experiences, 1):
        exp_id = exp.get('id')
        name = exp.get('name')
        exp_type = exp.get('type', 'experience').replace('-', ' ').title()
        duration = exp.get('duration', 'N/A')
        price = exp.get('price', 'N/A')
        description = exp.get('description', '')

        itinerary_text += f"**{i}. [{name}](/experiences?id={exp_id})**\n"
        itinerary_text += f"- Type: {exp_type} | Duration: {duration} | ${price}\n"
        itinerary_text += f"- {description[:150]}{'...' if len(description) > 150 else ''}\n\n"

    itinerary_text += "\n**Note:** Allow time between activities for meals, rest, and travel. Consider booking high-demand experiences in advance."

    return {
        'status': 'success',
        'message': itinerary_text,
        'experiences': selected_experiences
    }


def check_operating_hours(experience_id: str, date: str) -> Dict[str, Any]:
    """
    Get details for a specific experience including availability.

    Args:
        experience_id: Experience identifier
        date: Date to check (YYYY-MM-DD)

    Returns:
        Detailed experience information with link
    """
    # Fetch experience by ID from the travel service layer
    experience_model = get_experience_by_id(experience_id)
    if not experience_model:
        return {
            'status': 'not_found',
            'message': f'Experience with ID {experience_id} not found.',
            'experience_id': experience_id
        }
    experience = experience_model.model_dump()

    # Build detailed response
    name = experience.get('name')
    exp_type = experience.get('type', 'experience').replace('-', ' ').title()
    rating = experience.get('rating', 'N/A')
    price = experience.get('price', 'N/A')
    duration = experience.get('duration', 'N/A')
    city = experience.get('city', '')
    country = experience.get('country', '')
    description = experience.get('description', '')
    min_participants = experience.get('minParticipants', 1)
    max_participants = experience.get('maxParticipants', 'N/A')
    included_items = experience.get('includedItems', [])

    details_text = f"**[{name}](/experiences?id={experience_id})**\n\n"
    details_text += f"**Location:** {city}, {country}\n"
    details_text += f"**Type:** {exp_type} | **Rating:** {rating}★\n"
    details_text += f"**Duration:** {duration} | **Price:** ${price} per person\n"
    details_text += f"**Group Size:** {min_participants}-{max_participants} participants\n\n"
    details_text += f"**About:** {description}\n\n"

    if included_items:
        details_text += f"**What's Included:**\n"
        for item in included_items:
            details_text += f"- {item}\n"

    details_text += f"\n**Availability:** This experience is available for booking. Contact concierge for specific times on {date}.\n"
    details_text += f"\n[Book This Experience](/experiences?id={experience_id})"

    return {
        'status': 'success',
        'message': details_text,
        'experience': experience,
        'requested_date': date
    }
