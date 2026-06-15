"""Firestore-backed repository for user data."""

from datetime import datetime
from typing import Optional

from models.user import User
from services.firestore_client import get_client


def get_user_by_username(username: str) -> Optional[User]:
    db = get_client()
    docs = (
        db.collection("users")
        .where("username", "==", username)
        .limit(1)
        .stream()
    )
    for doc in docs:
        return User(**doc.to_dict())
    return None


def get_user_by_id(user_id: str) -> Optional[User]:
    db = get_client()
    doc = db.collection("users").document(user_id).get()
    if not doc.exists:
        return None
    return User(**doc.to_dict())


def save_user(user: User) -> User:
    """Upsert a user document. Sets updatedAt timestamp."""
    user.updatedAt = datetime.utcnow().isoformat()
    db = get_client()
    db.collection("users").document(user.id).set(user.model_dump(), merge=True)
    return user


def get_all_users() -> list[User]:
    """Return all users. Used only by the insecure concierge debug agent."""
    db = get_client()
    return [User(**doc.to_dict()) for doc in db.collection("users").stream()]
