from typing import List, Optional
from models.travel import Accommodation, Restaurant, Flight, Experience
import repositories.travel_repository as repo


# Accommodation operations
def get_all_accommodations(
    country: Optional[str] = None,
    type_: Optional[str] = None,
    affordability_tier: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
) -> List[Accommodation]:
    return repo.get_all_accommodations(
        country=country,
        type_=type_,
        affordability_tier=affordability_tier,
        min_price=min_price,
        max_price=max_price,
    )


def get_accommodation_by_id(accommodation_id: str) -> Optional[Accommodation]:
    return repo.get_accommodation_by_id(accommodation_id)


# Restaurant operations
def get_all_restaurants(
    country: Optional[str] = None,
    price_range: Optional[str] = None,
    affordability_tier: Optional[str] = None
) -> List[Restaurant]:
    return repo.get_all_restaurants(
        country=country,
        price_range=price_range,
        affordability_tier=affordability_tier,
    )


def get_restaurant_by_id(restaurant_id: str) -> Optional[Restaurant]:
    return repo.get_restaurant_by_id(restaurant_id)


# Flight operations
def get_all_flights(
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    class_: Optional[str] = None
) -> List[Flight]:
    return repo.get_all_flights(origin=origin, destination=destination, class_=class_)


def get_flight_by_id(flight_id: str) -> Optional[Flight]:
    return repo.get_flight_by_id(flight_id)


# Experience operations
def get_all_experiences(
    country: Optional[str] = None,
    type_: Optional[str] = None,
    affordability_tier: Optional[str] = None
) -> List[Experience]:
    return repo.get_all_experiences(
        country=country,
        type_=type_,
        affordability_tier=affordability_tier,
    )


def get_experience_by_id(experience_id: str) -> Optional[Experience]:
    return repo.get_experience_by_id(experience_id)
