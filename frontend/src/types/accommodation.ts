export type AccommodationType = 'hotel' | 'airbnb' | 'hostel' | 'villa';

export interface Accommodation {
  id: string;
  name: string;
  type: AccommodationType;
  country: string;
  city: string;
  address: string;
  rating: number; // 1-5 stars
  pricePerNight: number;
  amenities: string[];
  description: string;
  imageUrl: string; // Placeholder image URL
  maxGuests: number;
  bedrooms?: number;
  bathrooms?: number;
  availableFrom?: string; // ISO 8601
  availableTo?: string; // ISO 8601
}

export interface AccommodationFilters {
  country?: string;
  type?: AccommodationType;
  minPrice?: number;
  maxPrice?: number;
  minRating?: number;
}

export interface BookingRequest {
  accommodationId: string;
  checkInDate: string; // ISO 8601
  checkOutDate: string; // ISO 8601
  guests: number;
}

export interface BookingResponse {
  success: boolean;
  reservation: {
    id: string;
    accommodationName: string;
    totalAmount: number;
    nights: number;
    rewardPointsEarned: number;
  };
  updatedAvailableCredit: number;
  message: string;
}
