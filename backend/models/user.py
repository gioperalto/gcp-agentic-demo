from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal

class Address(BaseModel):
    street: str
    city: str
    state: str
    zipCode: str
    country: str

class User(BaseModel):
    id: str
    username: str
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
    createdAt: str
    updatedAt: str

class UserResponse(BaseModel):
    """User data returned to frontend (no password)"""
    id: str
    username: str
    email: EmailStr
    birthDate: str
    salary: float
    netWorth: float
    creditScore: int
    address: Address
    currentCard: Optional[Literal["legionnaire", "tribune"]]
    rejectionDate: Optional[str]
    interestRate: Optional[float]
