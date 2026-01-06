from pydantic import BaseModel, Field
from typing import Literal, Optional

class ApplicationData(BaseModel):
    salary: float
    netWorth: float
    creditScore: int = Field(ge=300, le=850)
    age: int

class Application(BaseModel):
    id: str
    userId: str
    cardSlug: Literal["legionnaire", "tribune"]
    status: Literal["approved", "rejected"]
    approvalTier: Literal["Highly Qualified", "Likely", "Unlikely"]
    interestRate: Optional[float]
    applicationDate: str  # ISO 8601
    userData: ApplicationData

class ApplicationRequest(BaseModel):
    cardSlug: Literal["legionnaire", "tribune"]

class ApplicationResponse(BaseModel):
    success: bool
    status: Literal["approved", "rejected"]
    approvalTier: Literal["Highly Qualified", "Likely", "Unlikely"]
    interestRate: Optional[float]
    message: str
    rejectionDate: Optional[str]  # Set if rejected
