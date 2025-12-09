"""
Tools for Travel Planner Agents
This module contains tool functions for flight search, accommodation search,
itinerary building, and budget management.
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
import random


# ============================================================================
# Flight Search Agent Tools
# ============================================================================

def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str = None,
    max_price: float = None,
    airline_preference: str = None,
    direct_only: bool = False
) -> Dict[str, Any]:
    """
    Search for available flights based on given criteria.

    Args:
        origin: Departure airport code or city
        destination: Arrival airport code or city
        departure_date: Departure date (YYYY-MM-DD)
        return_date: Return date for round trip (YYYY-MM-DD)
        max_price: Maximum price per person
        airline_preference: Preferred airline name
        direct_only: Only show direct flights

    Returns:
        Dictionary with flight options and details
    """
    # Mock flight data - in production, this would call real flight APIs
    flight_options = []

    airlines = ['United Airlines', 'Delta', 'American Airlines', 'Southwest', 'JetBlue']
    base_price = random.randint(250, 800)

    for i in range(3):
        airline = random.choice(airlines) if not airline_preference else airline_preference
        is_direct = direct_only or random.choice([True, False])

        flight = {
            'flight_number': f'{airline[:2].upper()}{random.randint(100, 999)}',
            'airline': airline,
            'origin': origin,
            'destination': destination,
            'departure_date': departure_date,
            'departure_time': f'{random.randint(6, 20):02d}:{random.choice(["00", "30"])}',
            'arrival_time': f'{random.randint(8, 22):02d}:{random.choice(["00", "30"])}',
            'duration': f'{random.randint(2, 8)}h {random.randint(0, 55)}m',
            'price': base_price + random.randint(-100, 200),
            'direct': is_direct,
            'stops': 0 if is_direct else random.randint(1, 2),
            'seats_available': random.randint(5, 50)
        }

        if return_date:
            flight['return_date'] = return_date
            flight['return_departure_time'] = f'{random.randint(6, 20):02d}:{random.choice(["00", "30"])}'
            flight['return_arrival_time'] = f'{random.randint(8, 22):02d}:{random.choice(["00", "30"])}'

        if max_price is None or flight['price'] <= max_price:
            flight_options.append(flight)

    return {
        'status': 'success',
        'search_criteria': {
            'origin': origin,
            'destination': destination,
            'departure_date': departure_date,
            'return_date': return_date
        },
        'options': flight_options,
        'total_results': len(flight_options)
    }


def compare_flight_prices(flight_ids: List[str]) -> Dict[str, Any]:
    """
    Compare prices and features of specific flights.

    Args:
        flight_ids: List of flight identifiers to compare

    Returns:
        Comparison data including best value, fastest, and cheapest options
    """
    return {
        'status': 'success',
        'comparison': {
            'cheapest': flight_ids[0] if flight_ids else None,
            'fastest': flight_ids[1] if len(flight_ids) > 1 else None,
            'best_value': flight_ids[0] if flight_ids else None
        },
        'recommendation': f'Best overall value: {flight_ids[0]}' if flight_ids else 'No flights to compare'
    }


# ============================================================================
# Accommodation Agent Tools
# ============================================================================

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


# ============================================================================
# Itinerary Builder Agent Tools
# ============================================================================

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
    preferences: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Create a detailed daily itinerary.

    Args:
        destination: City or location
        date: Date for the itinerary
        attractions: List of attraction IDs to include
        preferences: User preferences (pace, meal times, etc.)

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


# ============================================================================
# Budget Manager Agent Tools
# ============================================================================

def calculate_trip_cost(
    flight_cost: float = 0,
    accommodation_cost: float = 0,
    activities_cost: float = 0,
    food_cost: float = 0,
    transportation_cost: float = 0,
    miscellaneous: float = 0
) -> Dict[str, Any]:
    """
    Calculate total trip cost from various components.

    Args:
        flight_cost: Total flight costs
        accommodation_cost: Total accommodation costs
        activities_cost: Total activities and attractions costs
        food_cost: Estimated food costs
        transportation_cost: Local transportation costs
        miscellaneous: Other expenses

    Returns:
        Complete cost breakdown
    """
    total = flight_cost + accommodation_cost + activities_cost + food_cost + transportation_cost + miscellaneous

    return {
        'status': 'success',
        'breakdown': {
            'flights': flight_cost,
            'accommodation': accommodation_cost,
            'activities': activities_cost,
            'food': food_cost,
            'transportation': transportation_cost,
            'miscellaneous': miscellaneous
        },
        'total_cost': total,
        'per_category_percentage': {
            'flights': round((flight_cost / total * 100) if total > 0 else 0, 1),
            'accommodation': round((accommodation_cost / total * 100) if total > 0 else 0, 1),
            'activities': round((activities_cost / total * 100) if total > 0 else 0, 1),
            'food': round((food_cost / total * 100) if total > 0 else 0, 1),
            'transportation': round((transportation_cost / total * 100) if total > 0 else 0, 1),
            'miscellaneous': round((miscellaneous / total * 100) if total > 0 else 0, 1)
        }
    }


def check_budget_status(
    total_budget: float,
    current_spending: float
) -> Dict[str, Any]:
    """
    Check current spending against total budget.

    Args:
        total_budget: Total available budget
        current_spending: Current total spending

    Returns:
        Budget status and recommendations
    """
    remaining = total_budget - current_spending
    percentage_used = (current_spending / total_budget * 100) if total_budget > 0 else 0

    status = 'on_track'
    if percentage_used > 100:
        status = 'over_budget'
    elif percentage_used > 90:
        status = 'warning'

    return {
        'status': 'success',
        'budget_status': status,
        'total_budget': total_budget,
        'current_spending': current_spending,
        'remaining': remaining,
        'percentage_used': round(percentage_used, 1),
        'alert': 'Over budget! Consider cost-saving alternatives.' if status == 'over_budget' else
                 'Approaching budget limit.' if status == 'warning' else
                 'Budget is on track.'
    }


def suggest_cost_savings(
    category: str,
    current_cost: float,
    target_reduction: float
) -> Dict[str, Any]:
    """
    Suggest ways to reduce costs in a specific category.

    Args:
        category: Budget category (flights, accommodation, activities, food)
        current_cost: Current cost in this category
        target_reduction: Desired cost reduction amount

    Returns:
        Cost-saving suggestions
    """
    suggestions_map = {
        'flights': [
            'Consider flying on weekdays instead of weekends',
            'Book flights with one layover instead of direct',
            'Try alternative airports nearby',
            'Use flight comparison tools for better deals'
        ],
        'accommodation': [
            'Choose accommodations further from city center',
            'Consider hostels or vacation rentals instead of hotels',
            'Look for properties with free breakfast included',
            'Book refundable rates to watch for price drops'
        ],
        'activities': [
            'Look for free walking tours',
            'Visit museums on free admission days',
            'Use city passes for multiple attractions',
            'Enjoy free outdoor activities and parks'
        ],
        'food': [
            'Eat at local markets instead of restaurants',
            'Choose accommodations with kitchen facilities',
            'Have larger lunch and lighter dinner (lunch menus are cheaper)',
            'Look for happy hour deals'
        ]
    }

    return {
        'status': 'success',
        'category': category,
        'current_cost': current_cost,
        'target_reduction': target_reduction,
        'potential_new_cost': current_cost - target_reduction,
        'suggestions': suggestions_map.get(category, ['Consider budget alternatives'])
    }


def allocate_budget(
    total_budget: float,
    trip_duration_days: int,
    priorities: Dict[str, str] = None
) -> Dict[str, Any]:
    """
    Allocate budget across different travel categories.

    Args:
        total_budget: Total available budget
        trip_duration_days: Length of trip in days
        priorities: Dictionary of priorities (high, medium, low) for each category

    Returns:
        Recommended budget allocation
    """
    # Default allocation percentages
    default_allocation = {
        'flights': 0.35,
        'accommodation': 0.30,
        'food': 0.15,
        'activities': 0.15,
        'transportation': 0.03,
        'miscellaneous': 0.02
    }

    allocation = {}
    for category, percentage in default_allocation.items():
        allocation[category] = round(total_budget * percentage, 2)

    daily_budget = round(total_budget / trip_duration_days, 2) if trip_duration_days > 0 else 0

    return {
        'status': 'success',
        'total_budget': total_budget,
        'trip_duration_days': trip_duration_days,
        'allocation': allocation,
        'daily_budget': daily_budget,
        'daily_breakdown': {
            'accommodation': round(allocation['accommodation'] / trip_duration_days, 2) if trip_duration_days > 0 else 0,
            'food': round(allocation['food'] / trip_duration_days, 2) if trip_duration_days > 0 else 0,
            'activities': round(allocation['activities'] / trip_duration_days, 2) if trip_duration_days > 0 else 0
        }
    }
