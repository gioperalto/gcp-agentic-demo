from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
from models.auth import LoginRequest, LoginResponse
from models.user import UserResponse
from services.auth_service import create_access_token, get_current_user_id
from services.user_service import authenticate_user, get_user_by_id, to_user_response

router = APIRouter(prefix="/api/auth", tags=["authentication"])

def get_token_from_header(authorization: Optional[str] = Header(None)) -> str:
    """Extract JWT token from Authorization header"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    return authorization.replace("Bearer ", "")

async def get_current_user(token: str = Depends(get_token_from_header)) -> UserResponse:
    """Dependency to get current authenticated user"""
    user_id = get_current_user_id(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return to_user_response(user)

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Authenticate user and return JWT token"""
    user = authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Create JWT token
    access_token = create_access_token({"user_id": user.id})

    return LoginResponse(
        access_token=access_token,
        user=to_user_response(user)
    )

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    """Get current authenticated user"""
    return current_user
