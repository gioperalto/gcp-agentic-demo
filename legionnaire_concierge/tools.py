"""
Tools for the Legionnaire Concierge Agent
These tools provide access to local travel data for budget-conscious travelers
"""

import json
import os
from pathlib import Path

# Get the path to the data directory
DATA_DIR = Path(__file__).parent.parent / "backend" / "data"


def search_affordable_accommodations(country: str = None, city: str = None, max_price: int = None) -> str:
    """
    Search for budget and mid-range accommodations.

    Args:
        country: Filter by country (e.g., "Argentina", "Brazil", "Mexico", "Japan", "Spain", "Italy")
        city: Filter by city name
        max_price: Maximum price per night

    Returns:
        JSON string with accommodation details including id, name, type, city, price, and amenities
    """
    try:
        with open(DATA_DIR / "accommodations.json", "r") as f:
            data = json.load(f)

        # Filter for affordable options (budget and mid-range)
        results = [
            acc for acc in data
            if acc.get("affordabilityTier") in ["budget", "mid-range"]
        ]

        # Apply filters
        if country:
            results = [acc for acc in results if acc.get("country", "").lower() == country.lower()]

        if city:
            results = [acc for acc in results if acc.get("city", "").lower() == city.lower()]

        if max_price:
            results = [acc for acc in results if acc.get("pricePerNight", 999999) <= max_price]

        # Sort by price (lowest first)
        results.sort(key=lambda x: x.get("pricePerNight", 0))

        # Format results for agent
        formatted_results = []
        for acc in results:
            formatted_results.append({
                "id": acc.get("id"),
                "name": acc.get("name"),
                "type": acc.get("type"),
                "country": acc.get("country"),
                "city": acc.get("city"),
                "pricePerNight": acc.get("pricePerNight"),
                "rating": acc.get("rating"),
                "affordabilityTier": acc.get("affordabilityTier"),
                "description": acc.get("description"),
                "amenities": acc.get("amenities", []),
                "capacity": acc.get("capacity")
            })

        return json.dumps(formatted_results, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Failed to search accommodations: {str(e)}"})


def search_affordable_restaurants(country: str = None, city: str = None, max_price: int = None, cuisine: str = None) -> str:
    """
    Search for budget and mid-range restaurants.

    Args:
        country: Filter by country (e.g., "Argentina", "Brazil", "Mexico", "Japan", "Spain", "Italy")
        city: Filter by city name
        max_price: Maximum average price per person
        cuisine: Filter by cuisine type

    Returns:
        JSON string with restaurant details including id, name, city, cuisine, price, and specialties
    """
    try:
        with open(DATA_DIR / "restaurants.json", "r") as f:
            data = json.load(f)

        # Access the restaurants array
        restaurants = data.get("restaurants", [])

        # Filter for affordable options (budget and mid-range)
        results = [
            rest for rest in restaurants
            if rest.get("affordabilityTier") in ["budget", "mid-range"]
        ]

        # Apply filters
        if country:
            results = [rest for rest in results if rest.get("country", "").lower() == country.lower()]

        if city:
            results = [rest for rest in results if rest.get("city", "").lower() == city.lower()]

        if max_price:
            results = [rest for rest in results if rest.get("avgPricePerPerson", 999999) <= max_price]

        if cuisine:
            results = [rest for rest in results if cuisine.lower() in rest.get("cuisine", "").lower()]

        # Sort by price (lowest first)
        results.sort(key=lambda x: x.get("avgPricePerPerson", 0))

        # Format results for agent
        formatted_results = []
        for rest in results:
            formatted_results.append({
                "id": rest.get("id"),
                "name": rest.get("name"),
                "country": rest.get("country"),
                "city": rest.get("city"),
                "cuisine": rest.get("cuisine"),
                "priceRange": rest.get("priceRange"),
                "avgPricePerPerson": rest.get("avgPricePerPerson"),
                "rating": rest.get("rating"),
                "affordabilityTier": rest.get("affordabilityTier"),
                "description": rest.get("description"),
                "specialties": rest.get("specialties", []),
                "reservationAvailable": rest.get("reservationAvailable")
            })

        return json.dumps(formatted_results, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Failed to search restaurants: {str(e)}"})


def search_economy_flights(origin: str = None, destination: str = None, max_price: int = None) -> str:
    """
    Search for economy and premium-economy flights.

    Args:
        origin: Origin airport code (e.g., "JFK", "LAX", "MIA")
        destination: Destination airport code (e.g., "EZE", "GRU", "MEX", "NRT", "MAD", "FCO")
        max_price: Maximum flight price

    Returns:
        JSON string with flight details including id, airline, route, price, and class
    """
    try:
        with open(DATA_DIR / "flights.json", "r") as f:
            data = json.load(f)

        # Filter for economy and premium-economy classes
        results = [
            flight for flight in data
            if flight.get("class") in ["economy", "premium-economy"]
        ]

        # Apply filters
        if origin:
            results = [flight for flight in results if flight.get("origin", "").upper() == origin.upper()]

        if destination:
            results = [flight for flight in results if flight.get("destination", "").upper() == destination.upper()]

        if max_price:
            results = [flight for flight in results if flight.get("price", 999999) <= max_price]

        # Sort by price (lowest first)
        results.sort(key=lambda x: x.get("price", 0))

        # Format results for agent
        formatted_results = []
        for flight in results:
            formatted_results.append({
                "id": flight.get("id"),
                "airline": flight.get("airline"),
                "origin": flight.get("origin"),
                "destination": flight.get("destination"),
                "flightNumber": flight.get("flightNumber"),
                "class": flight.get("class"),
                "price": flight.get("price"),
                "duration": flight.get("duration"),
                "stops": flight.get("stops"),
                "departureDate": flight.get("departureDate"),
                "arrivalDate": flight.get("arrivalDate")
            })

        return json.dumps(formatted_results, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Failed to search flights: {str(e)}"})


def search_affordable_experiences(country: str = None, city: str = None, experience_type: str = None, max_price: int = None) -> str:
    """
    Search for budget and mid-range experiences and activities.

    Args:
        country: Filter by country (e.g., "Argentina", "Brazil", "Mexico", "Japan", "Spain", "Italy")
        city: Filter by city name
        experience_type: Filter by type (e.g., "hiking", "boat-tour", "winery-tour", "farm-to-table", "cultural", "atv")
        max_price: Maximum price per person

    Returns:
        JSON string with experience details including id, name, type, city, price, and description
    """
    try:
        with open(DATA_DIR / "experiences.json", "r") as f:
            data = json.load(f)

        # Filter for affordable options (budget and mid-range)
        results = [
            exp for exp in data
            if exp.get("affordabilityTier") in ["budget", "mid-range"]
        ]

        # Apply filters
        if country:
            results = [exp for exp in results if exp.get("country", "").lower() == country.lower()]

        if city:
            results = [exp for exp in results if exp.get("city", "").lower() == city.lower()]

        if experience_type:
            results = [exp for exp in results if exp.get("type", "").lower() == experience_type.lower()]

        if max_price:
            results = [exp for exp in results if exp.get("price", 999999) <= max_price]

        # Sort by price (lowest first)
        results.sort(key=lambda x: x.get("price", 0))

        # Format results for agent
        formatted_results = []
        for exp in results:
            formatted_results.append({
                "id": exp.get("id"),
                "name": exp.get("name"),
                "country": exp.get("country"),
                "city": exp.get("city"),
                "type": exp.get("type"),
                "price": exp.get("price"),
                "duration": exp.get("duration"),
                "rating": exp.get("rating"),
                "affordabilityTier": exp.get("affordabilityTier"),
                "description": exp.get("description"),
                "includedItems": exp.get("includedItems", []),
                "minParticipants": exp.get("minParticipants"),
                "maxParticipants": exp.get("maxParticipants")
            })

        return json.dumps(formatted_results, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Failed to search experiences: {str(e)}"})
