from fastapi import APIRouter
from services.feature_flag_service import evaluate_flag

router = APIRouter(prefix="/api/flags", tags=["feature-flags"])


@router.get("/evaluate/{flag_name}")
async def evaluate_feature_flag(flag_name: str):
    """Evaluate a feature flag via the Datadog OpenFeature provider.

    Flag state is managed in the Datadog UI — this endpoint exposes
    the current evaluation for debugging/monitoring purposes.
    """
    enabled = evaluate_flag(flag_name, default=False)
    return {"flag": flag_name, "enabled": enabled}
