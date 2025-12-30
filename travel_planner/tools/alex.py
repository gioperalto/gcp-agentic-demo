"""
Alex's Budget Management Tools
This module contains tool functions for budget management, cost calculation, and savings suggestions.
"""

from typing import Dict, Any
from .utils import format_budget_response


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
        Complete cost breakdown with a 'message' field containing formatted markdown.
        IMPORTANT: You MUST use the 'message' field verbatim in your response to users.
        It contains special preview:// links that enable interactive popups in the UI.
    """
    total = flight_cost + accommodation_cost + activities_cost + food_cost + transportation_cost + miscellaneous

    budget_data = {
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

    return {
        'status': 'success',
        'message': format_budget_response(budget_data),
        'data': budget_data
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
        Budget status and recommendations with a 'message' field containing formatted markdown.
        IMPORTANT: You MUST use the 'message' field verbatim in your response to users.
        It contains special preview:// links that enable interactive popups in the UI.
    """
    remaining = total_budget - current_spending
    percentage_used = (current_spending / total_budget * 100) if total_budget > 0 else 0

    status = 'on_track'
    if percentage_used > 100:
        status = 'over_budget'
    elif percentage_used > 90:
        status = 'warning'

    budget_data = {
        'budget_status': status,
        'total_budget': total_budget,
        'current_spending': current_spending,
        'remaining': remaining,
        'percentage_used': round(percentage_used, 1),
        'alert': 'Over budget! Consider cost-saving alternatives.' if status == 'over_budget' else
                 'Approaching budget limit.' if status == 'warning' else
                 'Budget is on track.'
    }

    return {
        'status': 'success',
        'message': format_budget_response(budget_data),
        'data': budget_data
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
    priorities: str = None
) -> Dict[str, Any]:
    """
    Allocate budget across different travel categories.

    Args:
        total_budget: Total available budget
        trip_duration_days: Length of trip in days
        priorities: JSON string of priorities (high, medium, low) for each category

    Returns:
        Recommended budget allocation with a 'message' field containing formatted markdown.
        IMPORTANT: You MUST use the 'message' field verbatim in your response to users.
        It contains special preview:// links that enable interactive popups in the UI.
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

    budget_data = {
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

    return {
        'status': 'success',
        'message': format_budget_response(budget_data),
        'data': budget_data
    }
