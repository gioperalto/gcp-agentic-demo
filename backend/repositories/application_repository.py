"""Firestore-backed repository for card application records."""

from typing import List

from models.application import Application
from services.firestore_client import get_client


def save_application(application: Application) -> None:
    db = get_client()
    db.collection("applications").document(application.id).set(application.model_dump())


def get_applications_by_user(user_id: str) -> List[Application]:
    db = get_client()
    docs = db.collection("applications").where("userId", "==", user_id).stream()
    return [Application(**doc.to_dict()) for doc in docs]
