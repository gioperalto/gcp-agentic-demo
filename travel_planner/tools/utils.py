"""
Utility functions for generating preview links in agent responses
"""

import json
from urllib.parse import quote
from typing import Dict, Any


def create_preview_link(label: str, data: Dict[str, Any], preview_type: str) -> str:
    """
    Create a markdown preview link that embeds data for frontend popup display.

    Args:
        label: The text to display for the link
        data: The data object to embed in the link
        preview_type: The type of preview (flight, accommodation, attraction, itinerary, budget)

    Returns:
        A markdown formatted link with embedded data

    Example:
        >>> create_preview_link("View Flight UA123", flight_data, "flight")
        "[View Flight UA123](preview://flight/{...encoded data...})"
    """
    # Convert data to JSON and URL encode it
    data_json = json.dumps(data, separators=(',', ':'))
    encoded_data = quote(data_json)

    # Create the preview link
    preview_link = f"[{label}](preview://{preview_type}/{encoded_data})"

    return preview_link


def format_flight_response(flights: list) -> str:
    """
    Format flight search results with preview links.

    Args:
        flights: List of flight dictionaries

    Returns:
        Formatted markdown string with preview links
    """
    if not flights:
        return "No flights found matching your criteria."

    response = f"I found {len(flights)} flight option(s) for you:\n\n"

    for i, flight in enumerate(flights, 1):
        # Format the stops info
        stops_info = 'Direct' if flight['direct'] else f"{flight['stops']} stop(s)"

        flight_summary = (
            f"{i}. **{flight['airline']}** {flight['flight_number']} - "
            f"${flight['price']} "
            f"({stops_info})\n"
            f"   Departs: {flight['departure_date']} at {flight['departure_time']}\n"
            f"   Duration: {flight['duration']}\n"
            f"   {create_preview_link('View Details', flight, 'flight')}\n\n"
        )
        response += flight_summary

    return response


def format_accommodation_response(accommodations: list) -> str:
    """
    Format accommodation search results with preview links.

    Args:
        accommodations: List of accommodation dictionaries

    Returns:
        Formatted markdown string with preview links
    """
    if not accommodations:
        return "No accommodations found matching your criteria."

    response = f"I found {len(accommodations)} accommodation option(s) for you:\n\n"

    for i, acc in enumerate(accommodations, 1):
        acc_summary = (
            f"{i}. **{acc['name']}** ({acc['type']})\n"
            f"   Rating: ⭐ {acc['rating']} ({acc['reviews_count']} reviews)\n"
            f"   Price: ${acc['price_per_night']}/night\n"
            f"   Location: {acc['distance_to_center']} from center\n"
            f"   {create_preview_link('View Details', acc, 'accommodation')}\n\n"
        )
        response += acc_summary

    return response


def format_attractions_response(attractions: list, destination: str) -> str:
    """
    Format attraction search results with preview links.

    Args:
        attractions: List of attraction dictionaries
        destination: Destination city/location

    Returns:
        Formatted markdown string with preview links
    """
    if not attractions:
        return f"No attractions found in {destination}."

    response = f"I found {len(attractions)} attraction(s) in {destination}:\n\n"

    for i, attr in enumerate(attractions, 1):
        price_str = "Free" if attr['price'] == 0 else f"${attr['price']}"
        attr_summary = (
            f"{i}. **{attr['name']}** ({attr['type']})\n"
            f"   Rating: ⭐ {attr['rating']}\n"
            f"   Price: {price_str} | Duration: {attr['duration']}\n"
            f"   Best time: {attr['best_time_to_visit']}\n"
            f"   {create_preview_link('View Details', attr, 'attraction')}\n\n"
        )
        response += attr_summary

    return response


def format_itinerary_response(itinerary_data: Dict[str, Any]) -> str:
    """
    Format daily itinerary with preview link.

    Args:
        itinerary_data: Dictionary containing itinerary details

    Returns:
        Formatted markdown string with preview link
    """
    response = f"**Daily Itinerary for {itinerary_data['date']} in {itinerary_data['destination']}**\n\n"
    response += f"Total Activities: {itinerary_data['total_activities']}\n"
    response += f"Estimated Cost: ${itinerary_data['estimated_cost']}\n\n"
    response += f"{create_preview_link('View Full Itinerary', itinerary_data, 'itinerary')}\n"

    return response


def format_budget_response(budget_data: Dict[str, Any]) -> str:
    """
    Format budget information with preview link.

    Args:
        budget_data: Dictionary containing budget details

    Returns:
        Formatted markdown string with preview link
    """
    if 'total_cost' in budget_data:
        # Trip cost calculation
        response = f"**Trip Cost Breakdown**\n\n"
        response += f"Total Cost: ${budget_data['total_cost']}\n\n"
        response += f"{create_preview_link('View Detailed Breakdown', budget_data, 'budget')}\n"
    elif 'budget_status' in budget_data:
        # Budget status check
        response = f"**Budget Status: {budget_data['budget_status'].upper()}**\n\n"
        response += f"Total Budget: ${budget_data['total_budget']}\n"
        response += f"Current Spending: ${budget_data['current_spending']}\n"
        response += f"Remaining: ${budget_data['remaining']}\n"
        response += f"Used: {budget_data['percentage_used']}%\n\n"
        response += f"_{budget_data['alert']}_\n\n"
        response += f"{create_preview_link('View Details', budget_data, 'budget')}\n"
    elif 'allocation' in budget_data:
        # Budget allocation
        response = f"**Budget Allocation for {budget_data['trip_duration_days']} days**\n\n"
        response += f"Total Budget: ${budget_data['total_budget']}\n"
        response += f"Daily Budget: ${budget_data['daily_budget']}\n\n"
        response += f"{create_preview_link('View Allocation Details', budget_data, 'budget')}\n"
    else:
        response = f"{create_preview_link('View Budget Details', budget_data, 'budget')}\n"

    return response


def format_restaurant_response(restaurants: list, destination: str) -> str:
    """
    Format restaurant recommendations with preview links.

    Args:
        restaurants: List of restaurant dictionaries
        destination: Destination city/location

    Returns:
        Formatted markdown string with preview links
    """
    if not restaurants:
        return f"No restaurants found in {destination}."

    response = f"I found {len(restaurants)} restaurant recommendation(s) in {destination}:\n\n"

    for i, rest in enumerate(restaurants, 1):
        reservation_str = "Reservation recommended" if rest['reservation_required'] else "Walk-ins welcome"
        rest_summary = (
            f"{i}. **{rest['name']}** ({rest['cuisine']})\n"
            f"   Rating: ⭐ {rest['rating']}\n"
            f"   Price Range: {rest['price_range']} | Avg: ${rest['average_cost_per_person']}/person\n"
            f"   {reservation_str}\n"
            f"   {create_preview_link('View Details', rest, 'restaurant')}\n\n"
        )
        response += rest_summary

    return response
