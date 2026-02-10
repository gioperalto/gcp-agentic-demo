"""
Jenny's Flight Search Tools
This module contains tool functions for flight search and comparison.
"""

import json
import os
from typing import Dict, List, Any


def _load_flights_data() -> List[Dict[str, Any]]:
    """Load flights data from JSON file."""
    data_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'backend', 'data', 'flights.json'
    )
    try:
        with open(data_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def search_flights(
    origin: str,
    destination: str,
    departure_date: str = None,
    return_date: str = None,
    max_price: float = None,
    airline_preference: str = None,
    direct_only: bool = False,
    include_premium: bool = True
) -> Dict[str, Any]:
    """
    Search for flights with emphasis on business and first class options.
    Tribune cardholders deserve premium travel experiences.

    Args:
        origin: Departure airport code or city
        destination: Arrival airport code or city
        departure_date: Departure date (YYYY-MM-DD)
        return_date: Return date for round trip (YYYY-MM-DD)
        max_price: Maximum price per person (optional - no financial restrictions)
        airline_preference: Preferred airline name
        direct_only: Only show direct flights
        include_premium: Include business and first class (default True)

    Returns:
        Dictionary with premium flight options and clickable links.
    """
    # Load flights from local data
    all_flights = _load_flights_data()

    # Filter by origin and destination
    matching_flights = [
        flight for flight in all_flights
        if flight.get('origin', '').upper() == origin.upper()
        and flight.get('destination', '').upper() == destination.upper()
    ]

    # If include_premium, prioritize business and first class
    if include_premium:
        premium_flights = [
            flight for flight in matching_flights
            if flight.get('class') in ['business', 'first', 'premium-economy']
        ]
        # If premium flights exist, show them; otherwise show all
        if premium_flights:
            filtered = premium_flights
        else:
            filtered = matching_flights
    else:
        filtered = matching_flights

    # Apply optional filters
    if departure_date:
        filtered = [f for f in filtered if departure_date in f.get('departureDate', '')]

    if airline_preference:
        airline_lower = airline_preference.lower()
        filtered = [f for f in filtered if airline_lower in f.get('airline', '').lower()]

    if direct_only:
        filtered = [f for f in filtered if f.get('stops', 0) == 0]

    if max_price:
        filtered = [f for f in filtered if f.get('price', 0) <= max_price]

    # Sort by class (first, business, premium-economy, economy) then by price
    class_priority = {'first': 0, 'business': 1, 'premium-economy': 2, 'economy': 3}
    filtered.sort(key=lambda x: (class_priority.get(x.get('class', 'economy'), 3), x.get('price', 0)))

    # Build response with clickable links
    if not filtered:
        return {
            'status': 'no_results',
            'message': f'No flights found from {origin} to {destination} matching your criteria. Consider adjusting your search parameters.',
            'filters_applied': {
                'origin': origin,
                'destination': destination,
                'departure_date': departure_date,
                'airline_preference': airline_preference,
                'direct_only': direct_only
            }
        }

    # Format results with links
    trip_type = "round trip" if return_date else "one way"
    results_text = f"I found **{len(filtered)} flights** from {origin} to {destination}:\n\n"

    for flight in filtered[:10]:  # Show top 10
        flight_id = flight.get('id')
        airline = flight.get('airline')
        flight_number = flight.get('flightNumber')
        flight_class = flight.get('class', 'economy').replace('-', ' ').title()
        price = flight.get('price', 'N/A')
        duration = flight.get('duration', 'N/A')
        stops = flight.get('stops', 0)
        stops_text = 'Nonstop' if stops == 0 else f'{stops} stop(s)'

        results_text += f"**[{airline} {flight_number} - {flight_class}](/flights?id={flight_id})**\n"
        results_text += f"- Price: ${price} | Duration: {duration} | {stops_text}\n"
        results_text += f"- Departure: {flight.get('departureDate', 'N/A')}\n\n"

    return {
        'status': 'success',
        'message': results_text,
        'flights': filtered[:10],
        'total_found': len(filtered)
    }


def compare_flight_prices(flight_ids: List[str]) -> Dict[str, Any]:
    """
    Compare specific flights side by side.

    Args:
        flight_ids: List of flight identifiers to compare

    Returns:
        Comparison of flight options with links
    """
    if not flight_ids:
        return {
            'status': 'error',
            'message': 'No flight identifiers provided to compare'
        }

    # Load flights from local data
    all_flights = _load_flights_data()

    # Find the specific flights
    flights_to_compare = [
        flight for flight in all_flights
        if flight.get('id') in flight_ids
    ]

    if not flights_to_compare:
        return {
            'status': 'not_found',
            'message': f'No flights found with the provided IDs: {", ".join(flight_ids)}'
        }

    # Build comparison
    results_text = f"**Flight Comparison** ({len(flights_to_compare)} flights):\n\n"

    for flight in flights_to_compare:
        flight_id = flight.get('id')
        airline = flight.get('airline')
        flight_number = flight.get('flightNumber')
        flight_class = flight.get('class', 'economy').replace('-', ' ').title()
        price = flight.get('price', 'N/A')
        duration = flight.get('duration', 'N/A')
        stops = flight.get('stops', 0)
        stops_text = 'Nonstop' if stops == 0 else f'{stops} stop(s)'

        results_text += f"**[{airline} {flight_number}](/flights?id={flight_id})**\n"
        results_text += f"- Class: {flight_class} | Price: ${price}\n"
        results_text += f"- Duration: {duration} | {stops_text}\n"
        results_text += f"- Route: {flight.get('origin')} → {flight.get('destination')}\n\n"

    results_text += "\n**Recommendation:** Consider business or first class for the ultimate comfort and service."

    return {
        'status': 'success',
        'message': results_text,
        'flights': flights_to_compare
    }


def get_flight_details(flight_id: str) -> Dict[str, Any]:
    """
    Get detailed information for a specific flight.

    Args:
        flight_id: Unique identifier for the flight

    Returns:
        Detailed flight information with link
    """
    # Load flights from local data
    all_flights = _load_flights_data()

    # Find the specific flight
    flight = next((f for f in all_flights if f.get('id') == flight_id), None)

    if not flight:
        return {
            'status': 'not_found',
            'message': f'Flight with ID {flight_id} not found.',
            'flight_id': flight_id
        }

    # Build detailed response
    airline = flight.get('airline')
    flight_number = flight.get('flightNumber')
    flight_class = flight.get('class', 'economy').replace('-', ' ').title()
    origin = flight.get('origin')
    destination = flight.get('destination')
    departure_date = flight.get('departureDate', 'N/A')
    arrival_date = flight.get('arrivalDate', 'N/A')
    price = flight.get('price', 'N/A')
    duration = flight.get('duration', 'N/A')
    stops = flight.get('stops', 0)
    stops_text = 'Nonstop' if stops == 0 else f'{stops} stop(s)'

    details_text = f"**[{airline} {flight_number}](/flights?id={flight_id})**\n\n"
    details_text += f"**Class:** {flight_class}\n"
    details_text += f"**Route:** {origin} → {destination}\n"
    details_text += f"**Departure:** {departure_date}\n"
    details_text += f"**Arrival:** {arrival_date}\n"
    details_text += f"**Duration:** {duration} | {stops_text}\n"
    details_text += f"**Price:** ${price} per person\n\n"

    if flight_class in ['First', 'Business']:
        details_text += f"**Premium Benefits:**\n"
        details_text += f"- Priority boarding and check-in\n"
        details_text += f"- Lounge access\n"
        details_text += f"- Extra baggage allowance\n"
        details_text += f"- Premium dining and beverages\n"
        details_text += f"- Lie-flat seats (on long-haul)\n\n"

    details_text += f"[Book This Flight](/flights?id={flight_id})"

    return {
        'status': 'success',
        'message': details_text,
        'flight': flight
    }
