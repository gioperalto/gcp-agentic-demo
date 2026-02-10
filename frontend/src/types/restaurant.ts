export interface Restaurant {
  id: string;
  name: string;
  country: string;
  city: string;
  address: string;
  cuisine: string;
  priceRange: '$' | '$$' | '$$$' | '$$$$';
  avgPricePerPerson: number;
  rating: number;
  imageUrl: string;
  description: string;
  specialties: string[];
  reservationAvailable: boolean;
  affordabilityTier: 'budget' | 'mid-range' | 'luxury';
}

export interface RestaurantReservation {
  restaurantId: string;
  restaurantName: string;
  numberOfPeople: number;
  date: string; // ISO 8601
  time: string; // HH:MM format
  specialRequests?: string;
}

export interface RestaurantFilters {
  country?: string;
  priceRange?: string[];
  cuisine?: string;
  affordabilityTier?: string;
  searchQuery?: string;
}
