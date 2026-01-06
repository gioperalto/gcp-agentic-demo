from fastapi import APIRouter, Depends, HTTPException
from models.application import ApplicationRequest, ApplicationResponse
from models.user import UserResponse
from services.application_service import process_application
from services.user_service import get_user_by_id
from routers.auth import get_current_user

router = APIRouter(prefix="/api/cards", tags=["cards"])

@router.post("/apply", response_model=ApplicationResponse)
async def apply_for_card(
    request: ApplicationRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Apply for a credit card"""
    # Get full user object (with password) for internal processing
    user = get_user_by_id(current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Process application
    result = process_application(user, request.cardSlug)
    return result
