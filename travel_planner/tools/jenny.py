"""
Jenny's Flight Search Tools
This module contains tool functions for flight search and comparison.
"""

from typing import Dict, List, Any


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
        Dictionary with search criteria to help the agent find real flight data online.
    """
    # Build search query components
    trip_type = "round trip" if return_date else "one way"
    price_constraint = f"under ${max_price}" if max_price else ""
    airline_constraint = f"on {airline_preference}" if airline_preference else ""
    direct_constraint = "direct flights only" if direct_only else ""

    # Construct helpful search guidance
    search_guidance = f"Search for {trip_type} flights from {origin} to {destination} departing on {departure_date}"
    if return_date:
        search_guidance += f" returning on {return_date}"

    constraints = [c for c in [price_constraint, airline_constraint, direct_constraint] if c]
    if constraints:
        search_guidance += f" ({', '.join(constraints)})"

    search_guidance += ". Look for current prices on flight booking websites like Google Flights, Kayak, Skyscanner, or airline websites."

    return {
        'status': 'search_required',
        'message': search_guidance,
        'search_criteria': {
            'origin': origin,
            'destination': destination,
            'departure_date': departure_date,
            'return_date': return_date,
            'max_price': max_price,
            'airline_preference': airline_preference,
            'direct_only': direct_only,
            'trip_type': trip_type
        },
        'suggested_sources': [
            'Google Flights',
            'Kayak',
            'Skyscanner',
            'Expedia',
            'Direct airline websites'
        ]
    }


def compare_flight_prices(flight_ids: List[str]) -> Dict[str, Any]:
    """
    Compare prices and features of specific flights.

    Args:
        flight_ids: List of flight identifiers to compare

    Returns:
        Guidance for comparing flight options
    """
    if not flight_ids:
        return {
            'status': 'error',
            'message': 'No flight identifiers provided to compare'
        }

    return {
        'status': 'search_required',
        'message': f'To compare these flights: {", ".join(flight_ids)}, search for each flight number on airline websites or flight comparison tools. Compare based on: total price, flight duration, number of stops, departure/arrival times, baggage allowance, and cancellation policies. Consider the best value based on your priorities (price vs convenience).',
        'flight_ids': flight_ids,
        'comparison_factors': [
            'Total price',
            'Flight duration',
            'Number of stops',
            'Departure/arrival times',
            'Baggage allowance',
            'Cancellation policy',
            'Airline reputation'
        ]
    }
