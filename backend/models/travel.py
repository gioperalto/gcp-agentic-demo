from pydantic import BaseModel, Field
from typing import Optional, List, Literal


class Accommodation(BaseModel):
    id: str
    name: str
    type: Literal["hotel", "airbnb", "hostel", "villa"]
    country: str
    city: str
    address: str
    rating: float = Field(ge=0, le=5)
    pricePerNight: float
    imageUrl: str
    description: str
    amenities: List[str]
    capacity: int
    affordabilityTier: Literal["budget", "mid-range", "luxury"]


class Restaurant(BaseModel):
    id: str
    name: str
    country: str
    city: str
    address: str
    cuisine: str
    priceRange: Literal["$", "$$", "$$$", "$$$$"]
    avgPricePerPerson: float
    rating: float = Field(ge=0, le=5)
    imageUrl: str
    description: str
    specialties: List[str]
    reservationAvailable: bool
    affordabilityTier: Literal["budget", "mid-range", "luxury"]


class Flight(BaseModel):
    id: str
    airline: str
    origin: str
    destination: str
    departureDate: str  # ISO 8601
    arrivalDate: str  # ISO 8601
    flightNumber: str
    class_: Literal["economy", "premium-economy", "business", "first", "private-jet"] = Field(alias="class")
    price: float
    duration: str
    stops: int
    imageUrl: str

    class Config:
        populate_by_name = True


class Experience(BaseModel):
    id: str
    name: str
    country: str
    city: str
    type: Literal["hiking", "atv", "boat-tour", "yacht", "winery-tour", "farm-to-table", "cultural", "adventure", "other"]
    price: float
    duration: str
    rating: float = Field(ge=0, le=5)
    imageUrl: str
    description: str
    minParticipants: int
    maxParticipants: int
    includedItems: List[str]
    affordabilityTier: Literal["budget", "mid-range", "luxury"]


class BookingRequest(BaseModel):
    userId: str
    type: Literal["accommodation", "restaurant", "flight", "experience"]
    itemId: str
    participants: int = 1
    usePoints: bool = False  # For flights, whether to use reward points
    nights: Optional[int] = None  # For accommodations


class RestaurantReservationRequest(BaseModel):
    restaurantId: str
    restaurantName: str
    numberOfPeople: int
    date: str
    time: str
    specialRequests: Optional[str] = None


class BookingResponse(BaseModel):
    success: bool
    message: str
    reservation: Optional[dict] = None
    updatedUser: Optional[dict] = None
