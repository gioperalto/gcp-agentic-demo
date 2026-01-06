import json
import uuid
from typing import Optional, List, Tuple, Literal
from datetime import datetime
from pathlib import Path
from models.application import Application, ApplicationData, ApplicationResponse
from models.user import User
from services.user_service import update_user
from data.cardData import CARD_THRESHOLDS

DATA_FILE = Path(__file__).parent.parent / "data" / "applications.json"

def _load_applications() -> List[Application]:
    """Load applications from JSON file"""
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)
    return [Application(**app) for app in data]

def _save_application(application: Application):
    """Save new application to JSON file"""
    applications = _load_applications()
    applications.append(application)
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump([app.model_dump() for app in applications], f, indent=2)

def calculate_age(birth_date: str) -> int:
    """Calculate age from birth date (YYYY-MM-DD)"""
    birth = datetime.fromisoformat(birth_date)
    today = datetime.utcnow()
    age = today.year - birth.year
    if today.month < birth.month or (today.month == birth.month and today.day < birth.day):
        age -= 1
    return age

def calculate_approval_tier(
    salary: float,
    net_worth: float,
    credit_score: int,
    age: int,
    card_slug: str
) -> Literal["Highly Qualified", "Likely", "Unlikely"]:
    """Calculate approval tier based on card thresholds"""
    thresholds = CARD_THRESHOLDS[card_slug]

    # Check highly qualified
    hq = thresholds["highlyQualified"]
    if (salary >= hq["minSalary"] and
        net_worth >= hq["minNetWorth"] and
        age >= hq["minAge"] and
        credit_score >= hq["minFico"]):
        return "Highly Qualified"

    # Check likely
    likely = thresholds["likely"]
    if (salary >= likely["minSalary"] and
        net_worth >= likely["minNetWorth"] and
        age >= likely["minAge"] and
        credit_score >= likely["minFico"]):
        return "Likely"

    return "Unlikely"

def calculate_interest_rate(
    approval_tier: str,
    card_slug: str
) -> Optional[float]:
    """Calculate interest rate based on approval tier"""
    # Legionnaire: 12.99% - 24.99%
    # Tribune: 4.99% - 9.99%

    if card_slug == "legionnaire":
        if approval_tier == "Highly Qualified":
            return 12.99
        elif approval_tier == "Likely":
            return 18.99
    elif card_slug == "tribune":
        if approval_tier == "Highly Qualified":
            return 4.99
        elif approval_tier == "Likely":
            return 7.49

    return None  # Unlikely tier doesn't get approved

def check_eligibility(user: User, card_slug: str) -> Tuple[bool, str]:
    """Check if user is eligible to apply"""

    # Check age (must be 18+)
    age = calculate_age(user.birthDate)
    if age < 18:
        return False, "You must be at least 18 years old to apply."

    # Check if user already has a card
    if user.currentCard:
        return False, f"You already have the {user.currentCard.title()} card. You can only hold one card at a time."

    # Check if user was recently rejected (60-day waiting period)
    if user.rejectionDate:
        rejection_date = datetime.fromisoformat(user.rejectionDate)
        days_since_rejection = (datetime.utcnow() - rejection_date).days
        if days_since_rejection < 60:
            days_remaining = 60 - days_since_rejection
            return False, f"You must wait {days_remaining} more days before applying again."

    return True, "Eligible"

def process_application(
    user: User,
    card_slug: str
) -> ApplicationResponse:
    """Process card application"""

    # Check eligibility
    eligible, message = check_eligibility(user, card_slug)
    if not eligible:
        return ApplicationResponse(
            success=False,
            status="rejected",
            approvalTier="Unlikely",
            interestRate=None,
            message=message,
            rejectionDate=None
        )

    # Calculate approval tier
    age = calculate_age(user.birthDate)
    approval_tier = calculate_approval_tier(
        user.salary,
        user.netWorth,
        user.creditScore,
        age,
        card_slug
    )

    # Determine approval status
    if approval_tier == "Unlikely":
        # Rejected
        user.rejectionDate = datetime.utcnow().isoformat()
        user.currentCard = None
        user.interestRate = None
        update_user(user)

        # Save application record
        application = Application(
            id=str(uuid.uuid4()),
            userId=user.id,
            cardSlug=card_slug,
            status="rejected",
            approvalTier=approval_tier,
            interestRate=None,
            applicationDate=datetime.utcnow().isoformat(),
            userData=ApplicationData(
                salary=user.salary,
                netWorth=user.netWorth,
                creditScore=user.creditScore,
                age=age
            )
        )
        _save_application(application)

        return ApplicationResponse(
            success=False,
            status="rejected",
            approvalTier=approval_tier,
            interestRate=None,
            message="Your application has been rejected. You may apply again in 60 days.",
            rejectionDate=user.rejectionDate
        )
    else:
        # Approved
        interest_rate = calculate_interest_rate(approval_tier, card_slug)
        user.currentCard = card_slug
        user.interestRate = interest_rate
        user.rejectionDate = None
        update_user(user)

        # Save application record
        application = Application(
            id=str(uuid.uuid4()),
            userId=user.id,
            cardSlug=card_slug,
            status="approved",
            approvalTier=approval_tier,
            interestRate=interest_rate,
            applicationDate=datetime.utcnow().isoformat(),
            userData=ApplicationData(
                salary=user.salary,
                netWorth=user.netWorth,
                creditScore=user.creditScore,
                age=age
            )
        )
        _save_application(application)

        return ApplicationResponse(
            success=True,
            status="approved",
            approvalTier=approval_tier,
            interestRate=interest_rate,
            message=f"Congratulations! You've been approved for the {card_slug.title()} card with an APR of {interest_rate}%.",
            rejectionDate=None
        )
