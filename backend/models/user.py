from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal, List

class Address(BaseModel):
    street: str
    city: str
    state: str
    zipCode: str
    country: str

class Reservation(BaseModel):
    id: str
    type: Literal["accommodation", "restaurant", "flight", "experience"]
    itemId: str
    itemName: str
    amount: float
    date: str  # ISO 8601
    participants: Optional[int] = 1
    status: Literal["confirmed", "pending", "cancelled"] = "confirmed"

class User(BaseModel):
    id: str
    username: str
    firstName: str
    lastName: str
    password: str  # Plain text for demo
    email: EmailStr
    birthDate: str  # YYYY-MM-DD format
    salary: float
    netWorth: float
    creditScore: int = Field(ge=300, le=850)
    address: Address
    currentCard: Optional[Literal["legionnaire", "tribune"]] = None
    rejectionDate: Optional[str] = None  # ISO 8601
    interestRate: Optional[float] = None
    creditLimit: Optional[float] = None
    availableCredit: Optional[float] = None
    rewardPoints: float = 0.0
    rewardPointsMultiplier: Optional[float] = None  # Points per dollar spent
    reservations: List[Reservation] = []
    createdAt: str
    updatedAt: str

class UserResponse(BaseModel):
    """User data returned to frontend (no password)"""
    id: str
    username: str
    firstName: str
    lastName: str
    email: EmailStr
    birthDate: str
    salary: float
    netWorth: float
    creditScore: int
    address: Address
    currentCard: Optional[Literal["legionnaire", "tribune"]]
    rejectionDate: Optional[str]
    interestRate: Optional[float]
    creditLimit: Optional[float]
    availableCredit: Optional[float]
    rewardPoints: float
    rewardPointsMultiplier: Optional[float]
    reservations: List[Reservation]
