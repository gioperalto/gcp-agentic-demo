from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime
import uuid

from models.travel import Accommodation
from models.user import UserResponse, Reservation
from services import travel_service
from services.user_service import get_user_by_id, update_user
from routers.auth import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/api/accommodations", tags=["accommodations"])


class BookingRequest(BaseModel):
    accommodationId: str
    paymentMethod: str  # 'card' or 'points'
    nights: int = 1
    checkInDate: str
    guests: int = 1


class BookingResponse(BaseModel):
    success: bool
    reservation: dict
    updatedUser: dict


@router.get("", response_model=List[Accommodation])
async def get_accommodations(
    country: Optional[str] = Query(None, description="Filter by country"),
    type: Optional[str] = Query(None, description="Filter by type (hotel, airbnb, hostel, villa)"),
    min_price: Optional[float] = Query(None, description="Minimum price per night"),
    max_price: Optional[float] = Query(None, description="Maximum price per night"),
    min_rating: Optional[float] = Query(None, description="Minimum rating")
):
    """Get all accommodations with optional filters"""
    return travel_service.get_all_accommodations(
        country=country,
        type_=type,
        min_price=min_price,
        max_price=max_price
    )


@router.get("/{accommodation_id}", response_model=Accommodation)
async def get_accommodation(accommodation_id: str):
    """Get a specific accommodation by ID"""
    accommodation = travel_service.get_accommodation_by_id(accommodation_id)
    if not accommodation:
        raise HTTPException(status_code=404, detail="Accommodation not found")
    return accommodation


@router.post("/book", response_model=BookingResponse)
async def book_accommodation(
    request: BookingRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Book an accommodation with either card credit or reward points

    Payment methods:
    - 'card': Deduct from available credit, earn reward points
    - 'points': Use reward points (100 points = $1), no additional points earned
    """
    # Get full user object (with password) for internal processing
    user = get_user_by_id(current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if user has a card
    if not user.currentCard:
        raise HTTPException(status_code=400, detail="You need a credit card to book accommodations")

    # Get accommodation details
    accommodation = travel_service.get_accommodation_by_id(request.accommodationId)
    if not accommodation:
        raise HTTPException(status_code=404, detail="Accommodation not found")

    # Calculate total cost
    total_cost = accommodation.pricePerNight * request.nights

    # Validate inputs
    if request.nights < 1:
        raise HTTPException(status_code=400, detail="Number of nights must be at least 1")
    if request.guests < 1:
        raise HTTPException(status_code=400, detail="Number of guests must be at least 1")

    # Process payment based on method
    if request.paymentMethod == 'card':
        # Check if user has sufficient credit
        if not user.availableCredit or user.availableCredit < total_cost:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient credit. Available: ${user.availableCredit or 0:.2f}, Required: ${total_cost:.2f}"
            )

        # Deduct from available credit
        user.availableCredit -= total_cost

        # Add reward points based on multiplier
        if user.rewardPointsMultiplier:
            points_earned = total_cost * user.rewardPointsMultiplier
            user.rewardPoints += points_earned

    elif request.paymentMethod == 'points':
        # Calculate points needed (100 points = $1)
        points_needed = total_cost * 100

        # Check if user has sufficient points
        if user.rewardPoints < points_needed:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient points. Available: {user.rewardPoints:.0f}, Required: {points_needed:.0f}"
            )

        # Deduct points
        user.rewardPoints -= points_needed

    else:
        raise HTTPException(status_code=400, detail="Invalid payment method. Use 'card' or 'points'")

    # Create reservation
    reservation = Reservation(
        id=str(uuid.uuid4()),
        type="accommodation",
        itemId=request.accommodationId,
        itemName=f"{accommodation.name} ({accommodation.city}, {accommodation.country})",
        amount=total_cost if request.paymentMethod == 'card' else 0.0,
        date=request.checkInDate,
        participants=request.guests,
        status="confirmed"
    )

    # Add reservation to user
    user.reservations.append(reservation)

    # Save updated user
    updated_user = update_user(user)

    return BookingResponse(
        success=True,
        reservation={
            "id": reservation.id,
            "accommodationId": request.accommodationId,
            "accommodationName": reservation.itemName,
            "amount": reservation.amount,
            "checkInDate": request.checkInDate,
            "nights": request.nights,
            "guests": request.guests,
            "status": reservation.status
        },
        updatedUser={
            "availableCredit": updated_user.availableCredit,
            "rewardPoints": updated_user.rewardPoints
        }
    )
