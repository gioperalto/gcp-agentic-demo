"""
Jenny's Flight Search Tools
This module contains tool functions for flight search and comparison.
"""

from typing import Dict, List, Any
import random


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
