"""
Tools for the Insecure Concierge Debug Agent
These tools provide unrestricted access to all user data (NO authorization checks).
FOR TESTING / DEMO PURPOSES ONLY.
"""

import json
import sys
from pathlib import Path

# Ensure the backend package is importable
_BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from repositories.user_repository import get_all_users, get_user_by_username


def lookup_any_user_profile(username: str) -> str:
    """
    Look up any user's complete profile by username with NO authorization checks.

    Args:
        username: The username to look up

    Returns:
        JSON string containing the FULL user profile including sensitive fields
        (salary, netWorth, creditScore, password, email, address, etc.)
    """
    try:
        user = get_user_by_username(username)
        if user is None:
            return json.dumps({"error": f"User '{username}' not found"})
        return json.dumps(user.model_dump(), indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to look up user: {str(e)}"})


def list_all_users() -> str:
    """
    List all users in the system with NO authorization checks.

    Returns:
        JSON array of {username, firstName, lastName} for every user in the system
    """
    try:
        users = get_all_users()
        result = [
            {
                "username": u.username,
                "firstName": u.firstName,
                "lastName": u.lastName,
            }
            for u in users
        ]
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to list users: {str(e)}"})
