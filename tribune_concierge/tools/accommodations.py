"""
Accommodation utilities and normalization functions
"""

import random
from typing import Optional

# Predefined accommodation types
ACCOMMODATION_TYPES = ['Hotel', 'Airbnb', 'Hostel', 'Villa']


def normalize_accommodation_type(accommodation_type: Optional[str]) -> str:
    """
    Normalize an accommodation type to match one of the predefined types.
    If no close match is found, returns 'Hotel' as default.

    Args:
        accommodation_type: The input accommodation type

    Returns:
        A normalized accommodation type from ACCOMMODATION_TYPES list
    """
    if not accommodation_type or accommodation_type.lower() == 'any':
        return random.choice(ACCOMMODATION_TYPES)

    # Convert to lowercase for comparison
    acc_lower = accommodation_type.lower()

    # Direct mapping for common variations
    accommodation_mapping = {
        'hotels': 'Hotel',
        'motel': 'Hotel',
        'motels': 'Hotel',
        'inn': 'Hotel',
        'resort': 'Hotel',
        'resorts': 'Hotel',
        'apartment': 'Airbnb',
        'apartments': 'Airbnb',
        'condo': 'Airbnb',
        'vacation rental': 'Airbnb',
        'rental': 'Airbnb',
        'bnb': 'Airbnb',
        'b&b': 'Airbnb',
        'hostels': 'Hostel',
        'backpacker': 'Hostel',
        'dorm': 'Hostel',
        'villas': 'Villa',
        'vacation home': 'Villa',
        'house': 'Villa',
        'cottage': 'Villa',
    }

    # Check direct mapping
    if acc_lower in accommodation_mapping:
        return accommodation_mapping[acc_lower]

    # Check if input matches any predefined type (case-insensitive)
    for acc_type in ACCOMMODATION_TYPES:
        if acc_type.lower() == acc_lower or acc_type.lower() in acc_lower or acc_lower in acc_type.lower():
            return acc_type

    # If no match found, return Hotel as default
    return 'Hotel'
