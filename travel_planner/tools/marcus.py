"""
Marcus's Accommodation Tools
This module contains tool functions for accommodation search and reviews.
"""

from typing import Dict, List, Any
import random


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
        accommodation_type: Type (hotel, airbnb, hostel, resort)
        max_price_per_night: Maximum price per night
        amenities: List of required amenities
        min_rating: Minimum rating (1-5)

    Returns:
        Dictionary with accommodation options
    """
    accommodation_types = ['Hotel', 'Airbnb', 'Resort', 'Hostel', 'Vacation Rental']
    accommodation_options = []

    for i in range(4):
        price = random.randint(50, 300)
        rating = round(random.uniform(3.5, 5.0), 1)

        accommodation = {
            'id': f'ACC{random.randint(1000, 9999)}',
            'name': f'{random.choice(["Grand", "Cozy", "Luxury", "Budget", "Boutique"])} {random.choice(["Hotel", "Inn", "Suites", "Lodge"])}',
            'type': random.choice(accommodation_types) if accommodation_type == 'any' else accommodation_type,
            'destination': destination,
            'price_per_night': price,
            'rating': rating,
            'reviews_count': random.randint(50, 500),
            'amenities': ['WiFi', 'Parking', 'Pool', 'Gym', 'Breakfast'],
            'distance_to_center': f'{random.uniform(0.5, 5.0):.1f} km',
            'check_in': check_in_date,
            'check_out': check_out_date,
            'available_rooms': random.randint(1, 10)
        }

        if (max_price_per_night is None or price <= max_price_per_night) and rating >= min_rating:
            accommodation_options.append(accommodation)

    return {
        'status': 'success',
        'search_criteria': {
            'destination': destination,
            'check_in': check_in_date,
            'check_out': check_out_date,
            'guests': guests
        },
        'options': accommodation_options,
        'total_results': len(accommodation_options)
    }


def get_accommodation_reviews(accommodation_id: str) -> Dict[str, Any]:
    """
    Get detailed reviews for a specific accommodation.

    Args:
        accommodation_id: Unique identifier for the accommodation

    Returns:
        Reviews and ratings breakdown
    """
    return {
        'status': 'success',
        'accommodation_id': accommodation_id,
        'overall_rating': round(random.uniform(4.0, 5.0), 1),
        'ratings_breakdown': {
            'cleanliness': round(random.uniform(4.0, 5.0), 1),
            'location': round(random.uniform(4.0, 5.0), 1),
            'value': round(random.uniform(3.5, 5.0), 1),
            'service': round(random.uniform(4.0, 5.0), 1)
        },
        'recent_reviews': [
            {'rating': 5, 'comment': 'Excellent location and very clean!'},
            {'rating': 4, 'comment': 'Great stay, would recommend.'},
            {'rating': 5, 'comment': 'Perfect for our family vacation.'}
        ]
    }
