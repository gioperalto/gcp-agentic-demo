"""
Marcus's Accommodation Tools
This module contains tool functions for accommodation search and reviews.
"""

import json
import os
from typing import Dict, List, Any, Optional
from .accommodations import normalize_accommodation_type


def _load_accommodations_data() -> List[Dict[str, Any]]:
    """Load accommodations data from JSON file."""
    data_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'backend', 'data', 'accommodations.json'
    )
    try:
        with open(data_path, 'r') as f:
            return json.load(f)
    except Exception:
        return []


def search_accommodations(
    destination: str,
    check_in_date: str = None,
    check_out_date: str = None,
    guests: int = 1,
    accommodation_type: str = 'any',
    max_price_per_night: float = None,
    amenities: List[str] = None,
    min_rating: float = 4.5
) -> Dict[str, Any]:
    """
    Search for luxury accommodations based on criteria.
    Focuses on 5-star hotels and luxury villas for Tribune cardholders.

    Args:
        destination: City or location
        check_in_date: Check-in date (YYYY-MM-DD)
        check_out_date: Check-out date (YYYY-MM-DD)
        guests: Number of guests
        accommodation_type: Type (hotel, airbnb, hostel, villa)
        max_price_per_night: Maximum price per night (optional - no financial restrictions assumed)
        amenities: List of required amenities
        min_rating: Minimum rating (1-5), defaults to 4.5 for luxury

    Returns:
        Dictionary with luxury accommodation options and clickable links.
    """
    # Load accommodations from local data
    all_accommodations = _load_accommodations_data()

    # Filter by destination (city)
    city_matches = [acc for acc in all_accommodations
                   if destination.lower() in acc.get('city', '').lower()
                   or destination.lower() in acc.get('country', '').lower()]

    # Focus on LUXURY accommodations: 5-star hotels and villas
    luxury_accommodations = [
        acc for acc in city_matches
        if acc.get('affordabilityTier') == 'luxury' and
        (acc.get('rating', 0) >= min_rating) and
        (acc.get('type') in ['hotel', 'villa'])
    ]

    # Apply optional filters
    filtered = luxury_accommodations

    if accommodation_type and accommodation_type.lower() != 'any':
        normalized_type = normalize_accommodation_type(accommodation_type).lower()
        filtered = [acc for acc in filtered if acc.get('type', '').lower() == normalized_type]

    if max_price_per_night:
        filtered = [acc for acc in filtered if acc.get('pricePerNight', 0) <= max_price_per_night]

    if guests:
        filtered = [acc for acc in filtered if acc.get('capacity', 0) >= guests]

    if amenities:
        filtered = [
            acc for acc in filtered
            if any(amenity.lower() in [a.lower() for a in acc.get('amenities', [])]
                  for amenity in amenities)
        ]

    # Sort by rating and price (highest first)
    filtered.sort(key=lambda x: (x.get('rating', 0), x.get('pricePerNight', 0)), reverse=True)

    # Build response with clickable links
    if not filtered:
        return {
            'status': 'no_results',
            'message': f'No luxury accommodations found in {destination} matching your criteria. Consider broadening your search.',
            'filters_applied': {
                'destination': destination,
                'min_rating': min_rating,
                'accommodation_type': accommodation_type,
                'guests': guests
            }
        }

    # Format results with links
    results_text = f"I found **{len(filtered)} exceptional luxury accommodations** in {destination}:\n\n"

    for acc in filtered[:10]:  # Show top 10
        acc_id = acc.get('id')
        name = acc.get('name')
        acc_type = acc.get('type', 'accommodation').capitalize()
        rating = acc.get('rating', 'N/A')
        price = acc.get('pricePerNight', 'N/A')
        description = acc.get('description', '')

        results_text += f"**[{name}](/accommodations?id={acc_id})**\n"
        results_text += f"- Type: {acc_type} | Rating: {rating}★ | ${price}/night\n"
        results_text += f"- {description[:120]}{'...' if len(description) > 120 else ''}\n\n"

    return {
        'status': 'success',
        'message': results_text,
        'accommodations': filtered[:10],
        'total_found': len(filtered)
    }


def get_accommodation_reviews(accommodation_id: str) -> Dict[str, Any]:
    """
    Get detailed information for a specific accommodation.

    Args:
        accommodation_id: Unique identifier for the accommodation

    Returns:
        Detailed accommodation information with link
    """
    # Load accommodations from local data
    all_accommodations = _load_accommodations_data()

    # Find the specific accommodation
    accommodation = next((acc for acc in all_accommodations if acc.get('id') == accommodation_id), None)

    if not accommodation:
        return {
            'status': 'not_found',
            'message': f'Accommodation with ID {accommodation_id} not found.',
            'accommodation_id': accommodation_id
        }

    # Build detailed response
    name = accommodation.get('name')
    acc_type = accommodation.get('type', 'accommodation').capitalize()
    rating = accommodation.get('rating', 'N/A')
    price = accommodation.get('pricePerNight', 'N/A')
    city = accommodation.get('city', '')
    country = accommodation.get('country', '')
    address = accommodation.get('address', '')
    description = accommodation.get('description', '')
    amenities = accommodation.get('amenities', [])
    capacity = accommodation.get('capacity', 'N/A')
    tier = accommodation.get('affordabilityTier', 'N/A')

    details_text = f"**[{name}](/accommodations?id={accommodation_id})**\n\n"
    details_text += f"**Location:** {city}, {country}\n"
    details_text += f"**Address:** {address}\n"
    details_text += f"**Type:** {acc_type} | **Rating:** {rating}★ | **Price:** ${price}/night\n"
    details_text += f"**Capacity:** {capacity} guests | **Tier:** {tier.capitalize()}\n\n"
    details_text += f"**About:** {description}\n\n"

    if amenities:
        details_text += f"**Amenities:**\n"
        for amenity in amenities[:10]:  # Show first 10 amenities
            details_text += f"- {amenity}\n"

    details_text += f"\n[View Full Details & Book](/accommodations?id={accommodation_id})"

    return {
        'status': 'success',
        'message': details_text,
        'accommodation': accommodation
    }
