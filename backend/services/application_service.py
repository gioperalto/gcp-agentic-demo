import uuid, random
from typing import Optional, Tuple, Literal
from datetime import datetime
from models.application import Application, ApplicationData, ApplicationResponse
from models.user import User
from services.user_service import update_user
from repositories.application_repository import save_application
from data.cardData import CARD_THRESHOLDS


def calculate_age(birth_date: str) -> int:
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
    thresholds = CARD_THRESHOLDS[card_slug]

    hq = thresholds["highlyQualified"]
    if (salary >= hq["minSalary"] and
        net_worth >= hq["minNetWorth"] and
        age >= hq["minAge"] and
        credit_score >= hq["minFico"]):
        return "Highly Qualified"

    likely = thresholds["likely"]
    if (salary >= likely["minSalary"] and
        net_worth >= likely["minNetWorth"] and
        age >= likely["minAge"] and
        credit_score >= likely["minFico"]):
        return "Likely"

    return "Unlikely"


def calculate_interest_rate(approval_tier: str, card_slug: str) -> Optional[float]:
    if card_slug == "legionnaire":
        if approval_tier == "Highly Qualified":
            return round(12.99 + random.uniform(0, 6.0), 2)
        elif approval_tier == "Likely":
            return round(18.99 + random.uniform(0, 6.0), 2)
    elif card_slug == "tribune":
        if approval_tier == "Highly Qualified":
            return round(4.99 + random.uniform(0, 5.0), 2)
        elif approval_tier == "Likely":
            return round(7.49 + random.uniform(0, 2.5), 2)
    return None


def check_eligibility(user: User, card_slug: str) -> Tuple[bool, str]:
    age = calculate_age(user.birthDate)
    if age < 18:
        return False, "You must be at least 18 years old to apply."

    if user.currentCard:
        return False, f"You already have the {user.currentCard.title()} card. You can only hold one card at a time."

    if user.rejectionDate:
        rejection_date = datetime.fromisoformat(user.rejectionDate)
        days_since_rejection = (datetime.utcnow() - rejection_date).days
        if days_since_rejection < 60:
            days_remaining = 60 - days_since_rejection
            return False, f"You must wait {days_remaining} more days before applying again."

    return True, "Eligible"


def process_application(user: User, card_slug: str) -> ApplicationResponse:
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

    age = calculate_age(user.birthDate)
    approval_tier = calculate_approval_tier(
        user.salary, user.netWorth, user.creditScore, age, card_slug
    )

    if approval_tier == "Unlikely":
        user.rejectionDate = datetime.utcnow().isoformat()
        user.currentCard = None
        user.interestRate = None
        update_user(user)

        save_application(Application(
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
        ))

        return ApplicationResponse(
            success=False,
            status="rejected",
            approvalTier=approval_tier,
            interestRate=None,
            message="Your application has been rejected. You may apply again in 60 days.",
            rejectionDate=user.rejectionDate
        )
    else:
        interest_rate = calculate_interest_rate(approval_tier, card_slug)
        user.currentCard = card_slug
        user.interestRate = interest_rate
        user.rejectionDate = None
        update_user(user)

        save_application(Application(
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
        ))

        return ApplicationResponse(
            success=True,
            status="approved",
            approvalTier=approval_tier,
            interestRate=interest_rate,
            message=f"Congratulations! You've been approved for the {card_slug.title()} card with an APR of {interest_rate}%.",
            rejectionDate=None
        )
