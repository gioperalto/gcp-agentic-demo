"""
Marcus's Accommodation Tools
This module contains tool functions for accommodation search and reviews.
"""

from typing import Dict, List, Any, Optional
from .accommodations import normalize_accommodation_type


def search_accommodations(
    destination: str,
    check_in_date: str,
    check_out_date: str,
    guests: int = 1,
    accommodation_type: str = 'any',
    max_price_per_night: float = None,
    amenities: List[str] = None,
    min_rating: float = 3.0
) -> Dict[str, Any]:
    """
    Search for accommodations based on criteria.

    Args:
        destination: City or location
        check_in_date: Check-in date (YYYY-MM-DD)
        check_out_date: Check-out date (YYYY-MM-DD)
        guests: Number of guests
        accommodation_type: Type (hotel, airbnb, hostel, villa)
        max_price_per_night: Maximum price per night
        amenities: List of required amenities
        min_rating: Minimum rating (1-5)

    Returns:
        Dictionary with search criteria to help the agent find real accommodation data online.
    """
    # Normalize the accommodation type to match predefined list
    normalized_type = normalize_accommodation_type(accommodation_type)

    # Build search query
    search_guidance = f"Search for {normalized_type.lower()} accommodations in {destination} for {guests} guest(s)"
    search_guidance += f" from {check_in_date} to {check_out_date}"

    constraints = []
    if max_price_per_night:
        constraints.append(f"maximum ${max_price_per_night} per night")
    if min_rating > 3.0:
        constraints.append(f"minimum {min_rating} star rating")
    if amenities:
        constraints.append(f"with amenities: {', '.join(amenities)}")

    if constraints:
        search_guidance += f" ({', '.join(constraints)})"

    search_guidance += ". Search on booking platforms like Booking.com, Airbnb, Hotels.com, Expedia, or hotel websites for current availability and pricing."

    return {
        'status': 'search_required',
        'message': search_guidance,
        'search_criteria': {
            'destination': destination,
            'check_in_date': check_in_date,
            'check_out_date': check_out_date,
            'guests': guests,
            'accommodation_type': normalized_type,
            'max_price_per_night': max_price_per_night,
            'amenities': amenities,
            'min_rating': min_rating
        },
        'suggested_sources': [
            'Booking.com',
            'Airbnb',
            'Hotels.com',
            'Expedia',
            'Agoda',
            'Hotel direct websites'
        ]
    }


def get_accommodation_reviews(accommodation_id: str) -> Dict[str, Any]:
    """
    Get detailed reviews for a specific accommodation.

    Args:
        accommodation_id: Unique identifier for the accommodation

    Returns:
        Guidance for finding reviews
    """
    return {
        'status': 'search_required',
        'message': f'To find reviews for accommodation {accommodation_id}, search for it on booking platforms like Booking.com, TripAdvisor, Google Reviews, or Airbnb. Look for: overall ratings, cleanliness ratings, location ratings, value for money, service quality, and recent guest reviews. Pay attention to both positive and negative feedback patterns.',
        'accommodation_id': accommodation_id,
        'review_aspects_to_check': [
            'Overall rating',
            'Cleanliness',
            'Location',
            'Value for money',
            'Service/Staff',
            'Amenities',
            'Recent reviews (last 3-6 months)',
            'Common complaints or praises'
        ]
    }
