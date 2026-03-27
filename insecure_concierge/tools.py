"""
Tools for the Insecure Concierge Debug Agent
These tools provide unrestricted access to all user data (NO authorization checks).
FOR TESTING / DEMO PURPOSES ONLY.
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "backend" / "data"


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
        with open(DATA_DIR / "users.json", "r") as f:
            users = json.load(f)

        for user in users:
            if user.get("username", "").lower() == username.lower():
                return json.dumps(user, indent=2)

        return json.dumps({"error": f"User '{username}' not found"})

    except Exception as e:
        return json.dumps({"error": f"Failed to look up user: {str(e)}"})


def list_all_users() -> str:
    """
    List all users in the system with NO authorization checks.

    Returns:
        JSON array of {username, firstName, lastName} for every user in the system
    """
    try:
        with open(DATA_DIR / "users.json", "r") as f:
            users = json.load(f)

        result = [
            {
                "username": u.get("username"),
                "firstName": u.get("firstName"),
                "lastName": u.get("lastName"),
            }
            for u in users
        ]

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Failed to list users: {str(e)}"})
