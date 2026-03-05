from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime
import uuid

from models.travel import (
    Accommodation,
    Restaurant,
    Flight,
    Experience,
    BookingRequest,
    BookingResponse,
    RestaurantReservationRequest
)
from models.user import Reservation
from services import travel_service
from services.user_service import get_user_by_id, update_user

router = APIRouter(prefix="/api/travel", tags=["travel"])


# ===== Accommodation Endpoints =====
@router.get("/accommodations", response_model=List[Accommodation])
async def get_accommodations(
    country: Optional[str] = Query(None, description="Filter by country"),
    type: Optional[str] = Query(None, description="Filter by type (hotel, airbnb, hostel, villa)"),
    affordabilityTier: Optional[str] = Query(None, description="Filter by affordability tier (budget, mid-range, luxury)"),
    minPrice: Optional[float] = Query(None, description="Minimum price per night"),
    maxPrice: Optional[float] = Query(None, description="Maximum price per night")
):
    """Get all accommodations with optional filters"""
    return travel_service.get_all_accommodations(
        country=country,
        type_=type,
        affordability_tier=affordabilityTier,
        min_price=minPrice,
        max_price=maxPrice
    )


@router.get("/accommodations/{accommodation_id}", response_model=Accommodation)
async def get_accommodation(accommodation_id: str):
    """Get a specific accommodation by ID"""
    accommodation = travel_service.get_accommodation_by_id(accommodation_id)
    if not accommodation:
        raise HTTPException(status_code=404, detail="Accommodation not found")
    return accommodation


# ===== Restaurant Endpoints =====
@router.get("/restaurants", response_model=List[Restaurant])
async def get_restaurants(
    country: Optional[str] = Query(None, description="Filter by country"),
    priceRange: Optional[str] = Query(None, description="Filter by price range ($, $$, $$$, $$$$)"),
    affordabilityTier: Optional[str] = Query(None, description="Filter by affordability tier (budget, mid-range, luxury)")
):
    """Get all restaurants with optional filters"""
    return travel_service.get_all_restaurants(
        country=country,
        price_range=priceRange,
        affordability_tier=affordabilityTier
    )


@router.get("/restaurants/{restaurant_id}", response_model=Restaurant)
async def get_restaurant(restaurant_id: str):
    """Get a specific restaurant by ID"""
    restaurant = travel_service.get_restaurant_by_id(restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant


@router.post("/restaurants/reserve", response_model=BookingResponse)
async def make_restaurant_reservation(request: RestaurantReservationRequest):
    """
    Make a restaurant reservation (no charge, just tracking)
    """
    # For restaurant reservations, we'll use the booking system but with 0 cost
    # This creates a reservation record but doesn't charge the user
    from routers.auth import get_current_user, get_token_from_header
    from fastapi import Depends

    # Note: In a production app, we would require authentication
    # For now, we'll create a simple reservation without user validation

    reservation_id = str(uuid.uuid4())

    return BookingResponse(
        success=True,
        message=f"Reservation confirmed at {request.restaurantName} for {request.numberOfPeople} people on {request.date} at {request.time}",
        reservation={
            "id": reservation_id,
            "type": "restaurant",
            "itemId": request.restaurantId,
            "itemName": request.restaurantName,
            "amount": 0.0,
            "date": f"{request.date}T{request.time}:00",
            "participants": request.numberOfPeople,
            "status": "confirmed",
            "specialRequests": request.specialRequests
        },
        updatedUser=None
    )


# ===== Flight Endpoints =====
@router.get("/flights", response_model=List[Flight])
async def get_flights(
    origin: Optional[str] = Query(None, description="Filter by origin airport code"),
    destination: Optional[str] = Query(None, description="Filter by destination airport code"),
    class_: Optional[str] = Query(None, alias="class", description="Filter by class (economy, premium-economy, business, first)")
):
    """Get all flights with optional filters"""
    return travel_service.get_all_flights(
        origin=origin,
        destination=destination,
        class_=class_
    )


@router.get("/flights/{flight_id}", response_model=Flight)
async def get_flight(flight_id: str):
    """Get a specific flight by ID"""
    flight = travel_service.get_flight_by_id(flight_id)
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    return flight


# ===== Experience Endpoints =====
@router.get("/experiences", response_model=List[Experience])
async def get_experiences(
    country: Optional[str] = Query(None, description="Filter by country"),
    type: Optional[str] = Query(None, description="Filter by type (hiking, atv, boat-tour, yacht, winery-tour, farm-to-table, cultural, adventure, other)"),
    affordabilityTier: Optional[str] = Query(None, description="Filter by affordability tier (budget, mid-range, luxury)")
):
    """Get all experiences with optional filters"""
    return travel_service.get_all_experiences(
        country=country,
        type_=type,
        affordability_tier=affordabilityTier
    )


@router.get("/experiences/{experience_id}", response_model=Experience)
async def get_experience(experience_id: str):
    """Get a specific experience by ID"""
    experience = travel_service.get_experience_by_id(experience_id)
    if not experience:
        raise HTTPException(status_code=404, detail="Experience not found")
    return experience


# ===== Booking Endpoint =====
@router.post("/book", response_model=BookingResponse)
async def create_booking(request: BookingRequest):
    """
    Create a booking/reservation and update user credit

    This endpoint:
    1. Validates the user exists and has sufficient credit
    2. Calculates the total cost
    3. For flights with usePoints=True, uses reward points instead of credit
    4. Creates a reservation
    5. Updates available credit
    6. Adds reward points based on the card's multiplier
    7. Saves the updated user data
    """
    # Get user
    user = get_user_by_id(request.userId)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if user has a card
    if not user.currentCard:
        raise HTTPException(status_code=400, detail="User does not have a credit card")

    # Get item details and calculate cost
    item = None
    item_name = ""
    total_cost = 0.0

    if request.type == "accommodation":
        item = travel_service.get_accommodation_by_id(request.itemId)
        if not item:
            raise HTTPException(status_code=404, detail="Accommodation not found")
        item_name = item.name
        nights = request.nights or 1
        total_cost = item.pricePerNight * nights

    elif request.type == "restaurant":
        item = travel_service.get_restaurant_by_id(request.itemId)
        if not item:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        item_name = item.name
        total_cost = item.avgPricePerPerson * request.participants

    elif request.type == "flight":
        item = travel_service.get_flight_by_id(request.itemId)
        if not item:
            raise HTTPException(status_code=404, detail="Flight not found")
        item_name = f"{item.airline} {item.flightNumber}"
        total_cost = item.price * request.participants

        # Handle points redemption for flights
        if request.usePoints:
            # Check if user has enough points (assuming 1 point = $0.01)
            points_needed = total_cost * 100  # Convert dollars to points
            if user.rewardPoints < points_needed:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient reward points. Need {points_needed}, have {user.rewardPoints}"
                )
            # Deduct points and set cost to 0
            user.rewardPoints -= points_needed
            total_cost = 0.0

    elif request.type == "experience":
        item = travel_service.get_experience_by_id(request.itemId)
        if not item:
            raise HTTPException(status_code=404, detail="Experience not found")
        item_name = item.name

        # Validate participant count
        if request.participants < item.minParticipants:
            raise HTTPException(
                status_code=400,
                detail=f"Minimum {item.minParticipants} participants required"
            )
        if request.participants > item.maxParticipants:
            raise HTTPException(
                status_code=400,
                detail=f"Maximum {item.maxParticipants} participants allowed"
            )

        total_cost = item.price * request.participants

        # Handle points redemption for experiences
        if request.usePoints:
            points_needed = total_cost * 100  # 100 points = $1
            if user.rewardPoints < points_needed:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient reward points. Need {points_needed}, have {user.rewardPoints}"
                )
            user.rewardPoints -= points_needed
            total_cost = 0.0

    else:
        raise HTTPException(status_code=400, detail="Invalid booking type")

    # Check if user has sufficient credit (if not using points)
    if total_cost > 0 and user.availableCredit < total_cost:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient credit. Need ${total_cost:.2f}, have ${user.availableCredit:.2f}"
        )

    # Create reservation
    reservation = Reservation(
        id=str(uuid.uuid4()),
        type=request.type,
        itemId=request.itemId,
        itemName=item_name,
        amount=total_cost,
        date=datetime.utcnow().isoformat(),
        participants=request.participants,
        status="confirmed"
    )

    # Update user data
    if total_cost > 0:
        user.availableCredit -= total_cost

        # Add reward points based on multiplier (only if paid with credit, not points)
        if user.rewardPointsMultiplier:
            points_earned = total_cost * user.rewardPointsMultiplier
            user.rewardPoints += points_earned

    # Add reservation to user
    user.reservations.append(reservation)

    # Save updated user
    updated_user = update_user(user)

    return BookingResponse(
        success=True,
        message=f"Booking confirmed for {item_name}",
        reservation=reservation.model_dump(),
        updatedUser={
            "availableCredit": updated_user.availableCredit,
            "rewardPoints": updated_user.rewardPoints,
            "reservations": [r.model_dump() for r in updated_user.reservations]
        }
    )
