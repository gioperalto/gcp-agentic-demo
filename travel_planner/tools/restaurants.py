"""
Restaurant utilities and normalization functions
"""

import random
from typing import Optional

# Predefined cuisine types
CUISINES = ['Italian', 'Japanese', 'Mexican', 'French', 'American', 'Thai']


def normalize_cuisine_type(cuisine_type: Optional[str]) -> str:
    """
    Normalize a cuisine type to match one of the predefined types.
    If no close match is found, returns a random cuisine.

    Args:
        cuisine_type: The input cuisine type

    Returns:
        A normalized cuisine type from CUISINES list
    """
    if not cuisine_type:
        return random.choice(CUISINES)

    # Convert to lowercase for comparison
    cuisine_lower = cuisine_type.lower()

    # Direct mapping for common variations
    cuisine_mapping = {
        'italy': 'Italian',
        'italia': 'Italian',
        'pasta': 'Italian',
        'pizza': 'Italian',
        'japan': 'Japanese',
        'sushi': 'Japanese',
        'ramen': 'Japanese',
        'mexico': 'Mexican',
        'tacos': 'Mexican',
        'tex-mex': 'Mexican',
        'france': 'French',
        'french cuisine': 'French',
        'usa': 'American',
        'us': 'American',
        'burger': 'American',
        'burgers': 'American',
        'steak': 'American',
        'thailand': 'Thai',
        'pad thai': 'Thai',
    }

    # Check direct mapping
    if cuisine_lower in cuisine_mapping:
        return cuisine_mapping[cuisine_lower]

    # Check if input matches any predefined cuisine (case-insensitive)
    for cuisine in CUISINES:
        if cuisine.lower() == cuisine_lower or cuisine.lower() in cuisine_lower or cuisine_lower in cuisine.lower():
            return cuisine

    # If no match found, return a random cuisine
    return random.choice(CUISINES)
