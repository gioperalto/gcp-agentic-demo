from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import datetime
import uuid

from models.travel import Flight
from models.user import UserResponse, Reservation
from services import travel_service
from services.user_service import get_user_by_id, update_user
from routers.auth import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/api/flights", tags=["flights"])


class FlightBookingRequest(BaseModel):
    flightId: str
    paymentMethod: str  # 'card' or 'points'
    passengers: int = 1


class FlightBookingResponse(BaseModel):
    success: bool
    reservation: dict
    updatedUser: dict


@router.get("", response_model=List[Flight])
async def get_flights():
    """Get all available flights"""
    return travel_service.get_all_flights()


@router.get("/{flight_id}", response_model=Flight)
async def get_flight(flight_id: str):
    """Get a specific flight by ID"""
    flight = travel_service.get_flight_by_id(flight_id)
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    return flight


@router.post("/book", response_model=FlightBookingResponse)
async def book_flight(
    request: FlightBookingRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Book a flight with either card credit or reward points

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
        raise HTTPException(status_code=400, detail="You need a credit card to book flights")

    # Get flight details
    flight = travel_service.get_flight_by_id(request.flightId)
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")

    # Calculate total cost
    total_cost = flight.price * request.passengers

    # Validate passengers
    if request.passengers < 1 or request.passengers > 9:
        raise HTTPException(status_code=400, detail="Number of passengers must be between 1 and 9")

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
        type="flight",
        itemId=request.flightId,
        itemName=f"{flight.airline} {flight.flightNumber} ({flight.origin} → {flight.destination})",
        amount=total_cost if request.paymentMethod == 'card' else 0.0,
        date=flight.departureDate,
        participants=request.passengers,
        status="confirmed"
    )

    # Add reservation to user
    user.reservations.append(reservation)

    # Save updated user
    updated_user = update_user(user)

    return FlightBookingResponse(
        success=True,
        reservation={
            "id": reservation.id,
            "flightId": request.flightId,
            "flightName": reservation.itemName,
            "amount": reservation.amount,
            "date": reservation.date,
            "passengers": request.passengers,
            "status": reservation.status
        },
        updatedUser={
            "availableCredit": updated_user.availableCredit,
            "rewardPoints": updated_user.rewardPoints
        }
    )
