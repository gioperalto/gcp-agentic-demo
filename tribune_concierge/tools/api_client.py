"""
Shared API client for Tribune Concierge agent tools.
All tools fetch data from the backend API instead of reading JSON files directly.
"""

import os
from typing import Any, Dict, List, Optional

import httpx

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def api_get(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
    """
    Make a GET request to the backend API.

    Args:
        endpoint: API endpoint path (e.g., "/api/travel/flights")
        params: Optional query parameters

    Returns:
        Parsed JSON response

    Raises:
        httpx.HTTPStatusError: If the API returns an error status code
    """
    url = f"{API_BASE_URL}{endpoint}"
    # Filter out None values from params
    if params:
        params = {k: v for k, v in params.items() if v is not None}
    response = httpx.get(url, params=params, timeout=10.0)
    response.raise_for_status()
    return response.json()
