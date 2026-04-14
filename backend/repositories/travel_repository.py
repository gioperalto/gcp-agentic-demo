"""
Firestore-backed repository for travel catalog data.

All filtering is done in-memory after a full collection fetch.
This is appropriate for the demo dataset size (~200 items per collection)
and avoids the need for composite Firestore indexes.

imageUrl fields are resolved to signed GCS URLs at read time via storage_client.
"""

from typing import List, Optional

from models.travel import Accommodation, Experience, Flight, Restaurant
from services.firestore_client import get_client
from services.storage_client import resolve_image_url


def _resolve(doc_data: dict) -> dict:
    if "imageUrl" in doc_data:
        doc_data["imageUrl"] = resolve_image_url(doc_data["imageUrl"])
    return doc_data


# ---------------------------------------------------------------------------
# Accommodations
# ---------------------------------------------------------------------------

def get_all_accommodations(
    country: Optional[str] = None,
    type_: Optional[str] = None,
    affordability_tier: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
) -> List[Accommodation]:
    db = get_client()
    items = [Accommodation(**_resolve(doc.to_dict())) for doc in db.collection("accommodations").stream()]

    if country:
        items = [a for a in items if a.country.lower() == country.lower()]
    if type_:
        items = [a for a in items if a.type == type_]
    if affordability_tier:
        items = [a for a in items if a.affordabilityTier == affordability_tier]
    if min_price is not None:
        items = [a for a in items if a.pricePerNight >= min_price]
    if max_price is not None:
        items = [a for a in items if a.pricePerNight <= max_price]
    return items


def get_accommodation_by_id(accommodation_id: str) -> Optional[Accommodation]:
    db = get_client()
    doc = db.collection("accommodations").document(accommodation_id).get()
    if not doc.exists:
        return None
    return Accommodation(**_resolve(doc.to_dict()))


# ---------------------------------------------------------------------------
# Restaurants
# ---------------------------------------------------------------------------

def get_all_restaurants(
    country: Optional[str] = None,
    price_range: Optional[str] = None,
    affordability_tier: Optional[str] = None,
) -> List[Restaurant]:
    db = get_client()
    items = [Restaurant(**_resolve(doc.to_dict())) for doc in db.collection("restaurants").stream()]

    if country:
        items = [r for r in items if r.country.lower() == country.lower()]
    if price_range:
        items = [r for r in items if r.priceRange == price_range]
    if affordability_tier:
        items = [r for r in items if r.affordabilityTier == affordability_tier]
    return items


def get_restaurant_by_id(restaurant_id: str) -> Optional[Restaurant]:
    db = get_client()
    doc = db.collection("restaurants").document(restaurant_id).get()
    if not doc.exists:
        return None
    return Restaurant(**_resolve(doc.to_dict()))


# ---------------------------------------------------------------------------
# Flights
# ---------------------------------------------------------------------------

def get_all_flights(
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    class_: Optional[str] = None,
) -> List[Flight]:
    db = get_client()
    items = [Flight(**_resolve(doc.to_dict())) for doc in db.collection("flights").stream()]

    if origin:
        items = [f for f in items if f.origin.lower() == origin.lower()]
    if destination:
        items = [f for f in items if f.destination.lower() == destination.lower()]
    if class_:
        items = [f for f in items if f.class_ == class_]
    return items


def get_flight_by_id(flight_id: str) -> Optional[Flight]:
    db = get_client()
    doc = db.collection("flights").document(flight_id).get()
    if not doc.exists:
        return None
    return Flight(**_resolve(doc.to_dict()))


# ---------------------------------------------------------------------------
# Experiences
# ---------------------------------------------------------------------------

def get_all_experiences(
    country: Optional[str] = None,
    type_: Optional[str] = None,
    affordability_tier: Optional[str] = None,
) -> List[Experience]:
    db = get_client()
    items = [Experience(**_resolve(doc.to_dict())) for doc in db.collection("experiences").stream()]

    if country:
        items = [e for e in items if e.country.lower() == country.lower()]
    if type_:
        items = [e for e in items if e.type == type_]
    if affordability_tier:
        items = [e for e in items if e.affordabilityTier == affordability_tier]
    return items


def get_experience_by_id(experience_id: str) -> Optional[Experience]:
    db = get_client()
    doc = db.collection("experiences").document(experience_id).get()
    if not doc.exists:
        return None
    return Experience(**_resolve(doc.to_dict()))
