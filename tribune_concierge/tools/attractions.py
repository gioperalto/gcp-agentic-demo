"""
Attraction utilities and normalization functions
"""

import random
from typing import Optional

# Predefined attraction types
ATTRACTION_TYPES = ['Museum', 'Park', 'Restaurant', 'Monument', 'Beach', 'Market', 'Gallery']


def normalize_attraction_type(attraction_type: Optional[str]) -> str:
    """
    Normalize an attraction type to match one of the predefined types.
    If no close match is found, returns a random attraction type.

    Args:
        attraction_type: The input attraction type

    Returns:
        A normalized attraction type from ATTRACTION_TYPES list
    """
    if not attraction_type:
        return random.choice(ATTRACTION_TYPES)

    # Convert to lowercase for comparison
    attr_lower = attraction_type.lower()

    # Direct mapping for common variations
    attraction_mapping = {
        'museums': 'Museum',
        'art museum': 'Museum',
        'history museum': 'Museum',
        'science museum': 'Museum',
        'exhibition': 'Museum',
        'parks': 'Park',
        'garden': 'Park',
        'gardens': 'Park',
        'nature': 'Park',
        'botanical garden': 'Park',
        'national park': 'Park',
        'restaurants': 'Restaurant',
        'dining': 'Restaurant',
        'cafe': 'Restaurant',
        'cafes': 'Restaurant',
        'food': 'Restaurant',
        'monuments': 'Monument',
        'memorial': 'Monument',
        'statue': 'Monument',
        'landmark': 'Monument',
        'historic site': 'Monument',
        'beaches': 'Beach',
        'seaside': 'Beach',
        'coast': 'Beach',
        'shore': 'Beach',
        'markets': 'Market',
        'bazaar': 'Market',
        'shopping': 'Market',
        'street market': 'Market',
        'flea market': 'Market',
        'galleries': 'Gallery',
        'art gallery': 'Gallery',
        'exhibition hall': 'Gallery',
    }

    # Check direct mapping
    if attr_lower in attraction_mapping:
        return attraction_mapping[attr_lower]

    # Check if input matches any predefined type (case-insensitive)
    for attr_type in ATTRACTION_TYPES:
        if attr_type.lower() == attr_lower or attr_type.lower() in attr_lower or attr_lower in attr_type.lower():
            return attr_type

    # If no match found, return a random attraction type
    return random.choice(ATTRACTION_TYPES)
