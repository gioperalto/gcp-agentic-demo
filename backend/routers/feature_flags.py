"""
Feature Flags Router
Provides REST endpoints for reading and updating feature flag state.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from services.feature_flag_service import evaluate_flag, set_flag, get_all_flags

router = APIRouter(prefix="/api/flags", tags=["feature-flags"])


class FlagUpdateRequest(BaseModel):
    enabled: bool


@router.get("")
async def list_flags():
    """Return all feature flags and their current state."""
    return get_all_flags()


@router.put("/{flag_name}")
async def update_flag(flag_name: str, body: FlagUpdateRequest):
    """Update a feature flag's enabled state."""
    return set_flag(flag_name, body.enabled)


@router.get("/evaluate/{flag_name}")
async def evaluate_flag_endpoint(flag_name: str):
    """Evaluate a single feature flag and return its resolved value."""
    result = evaluate_flag(flag_name)
    return {"flag": flag_name, "enabled": result}
