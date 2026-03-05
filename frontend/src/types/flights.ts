export interface Flight {
  id: string;
  airline: string;
  origin: string;
  destination: string;
  departureDate: string; // ISO 8601
  arrivalDate: string; // ISO 8601
  flightNumber: string;
  class: 'economy' | 'premium-economy' | 'business' | 'first' | 'private-jet';
  price: number;
  duration: string;
  stops: number;
  imageUrl: string;
}

export interface FlightFilters {
  destinationCountry: string;
  flightClass: string;
  minPrice: number;
  maxPrice: number;
}

export interface FlightBookingRequest {
  flightId: string;
  paymentMethod: 'card' | 'points';
  passengers: number;
}

export interface FlightBookingResponse {
  success: boolean;
  reservation: {
    id: string;
    flightId: string;
    flightName: string;
    amount: number;
    date: string;
    passengers: number;
    status: 'confirmed' | 'pending' | 'cancelled';
  };
  updatedUser: {
    availableCredit?: number;
    rewardPoints: number;
  };
}
