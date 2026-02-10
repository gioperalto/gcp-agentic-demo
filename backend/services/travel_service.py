import json
from typing import List, Optional
from pathlib import Path
from models.travel import Accommodation, Restaurant, Flight, Experience

# Data file paths
DATA_DIR = Path(__file__).parent.parent / "data"
ACCOMMODATIONS_FILE = DATA_DIR / "accommodations.json"
RESTAURANTS_FILE = DATA_DIR / "restaurants.json"
FLIGHTS_FILE = DATA_DIR / "flights.json"
EXPERIENCES_FILE = DATA_DIR / "experiences.json"


def _load_accommodations() -> List[Accommodation]:
    """Load accommodations from JSON file"""
    if not ACCOMMODATIONS_FILE.exists():
        return []
    with open(ACCOMMODATIONS_FILE, 'r') as f:
        data = json.load(f)
    return [Accommodation(**item) for item in data]


def _load_restaurants() -> List[Restaurant]:
    """Load restaurants from JSON file"""
    if not RESTAURANTS_FILE.exists():
        return []
    with open(RESTAURANTS_FILE, 'r') as f:
        data = json.load(f)
    # The restaurants file has a "restaurants" wrapper
    restaurants_data = data.get("restaurants", [])
    return [Restaurant(**item) for item in restaurants_data]


def _load_flights() -> List[Flight]:
    """Load flights from JSON file"""
    if not FLIGHTS_FILE.exists():
        return []
    with open(FLIGHTS_FILE, 'r') as f:
        data = json.load(f)
    return [Flight(**item) for item in data]


def _load_experiences() -> List[Experience]:
    """Load experiences from JSON file"""
    if not EXPERIENCES_FILE.exists():
        return []
    with open(EXPERIENCES_FILE, 'r') as f:
        data = json.load(f)
    return [Experience(**item) for item in data]


# Accommodation operations
def get_all_accommodations(
    country: Optional[str] = None,
    type_: Optional[str] = None,
    affordability_tier: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
) -> List[Accommodation]:
    """Get all accommodations with optional filters"""
    accommodations = _load_accommodations()

    if country:
        accommodations = [a for a in accommodations if a.country.lower() == country.lower()]
    if type_:
        accommodations = [a for a in accommodations if a.type == type_]
    if affordability_tier:
        accommodations = [a for a in accommodations if a.affordabilityTier == affordability_tier]
    if min_price is not None:
        accommodations = [a for a in accommodations if a.pricePerNight >= min_price]
    if max_price is not None:
        accommodations = [a for a in accommodations if a.pricePerNight <= max_price]

    return accommodations


def get_accommodation_by_id(accommodation_id: str) -> Optional[Accommodation]:
    """Get a specific accommodation by ID"""
    accommodations = _load_accommodations()
    return next((a for a in accommodations if a.id == accommodation_id), None)


# Restaurant operations
def get_all_restaurants(
    country: Optional[str] = None,
    price_range: Optional[str] = None,
    affordability_tier: Optional[str] = None
) -> List[Restaurant]:
    """Get all restaurants with optional filters"""
    restaurants = _load_restaurants()

    if country:
        restaurants = [r for r in restaurants if r.country.lower() == country.lower()]
    if price_range:
        restaurants = [r for r in restaurants if r.priceRange == price_range]
    if affordability_tier:
        restaurants = [r for r in restaurants if r.affordabilityTier == affordability_tier]

    return restaurants


def get_restaurant_by_id(restaurant_id: str) -> Optional[Restaurant]:
    """Get a specific restaurant by ID"""
    restaurants = _load_restaurants()
    return next((r for r in restaurants if r.id == restaurant_id), None)


# Flight operations
def get_all_flights(
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    class_: Optional[str] = None
) -> List[Flight]:
    """Get all flights with optional filters"""
    flights = _load_flights()

    if origin:
        flights = [f for f in flights if f.origin.lower() == origin.lower()]
    if destination:
        flights = [f for f in flights if f.destination.lower() == destination.lower()]
    if class_:
        flights = [f for f in flights if f.class_ == class_]

    return flights


def get_flight_by_id(flight_id: str) -> Optional[Flight]:
    """Get a specific flight by ID"""
    flights = _load_flights()
    return next((f for f in flights if f.id == flight_id), None)


# Experience operations
def get_all_experiences(
    country: Optional[str] = None,
    type_: Optional[str] = None,
    affordability_tier: Optional[str] = None
) -> List[Experience]:
    """Get all experiences with optional filters"""
    experiences = _load_experiences()

    if country:
        experiences = [e for e in experiences if e.country.lower() == country.lower()]
    if type_:
        experiences = [e for e in experiences if e.type == type_]
    if affordability_tier:
        experiences = [e for e in experiences if e.affordabilityTier == affordability_tier]

    return experiences


def get_experience_by_id(experience_id: str) -> Optional[Experience]:
    """Get a specific experience by ID"""
    experiences = _load_experiences()
    return next((e for e in experiences if e.id == experience_id), None)
