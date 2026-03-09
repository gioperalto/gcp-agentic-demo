import type { ChatEvent } from '../types/chat';
import type { User, LoginRequest, LoginResponse } from '../types/user';
import type { ApplicationRequest, ApplicationResponse } from '../types/application';
import type { Flight, FlightBookingRequest, FlightBookingResponse } from '../types/flights';
import type { Accommodation, AccommodationFilters, BookingRequest, BookingResponse } from '../types/accommodation';
import type { Experience, ExperienceBookingRequest, ExperienceBookingResponse } from '../types/experience';
import type { Restaurant, RestaurantReservation } from '../types/restaurant';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Token storage
let authToken: string | null = localStorage.getItem('auth_token');

export function setAuthToken(token: string | null) {
  authToken = token;
  if (token) {
    localStorage.setItem('auth_token', token);
  } else {
    localStorage.removeItem('auth_token');
  }
}

export function getAuthToken(): string | null {
  return authToken;
}

function getHeaders(): HeadersInit {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }

  return headers;
}

// Authentication endpoints
export async function login(credentials: LoginRequest): Promise<LoginResponse> {
  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(credentials),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Login failed');
  }

  const data: LoginResponse = await response.json();
  setAuthToken(data.access_token);
  return data;
}

export async function getCurrentUser(): Promise<User> {
  const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
    headers: getHeaders(),
  });

  if (!response.ok) {
    if (response.status === 401) {
      setAuthToken(null);
      throw new Error('Not authenticated');
    }
    throw new Error('Failed to fetch user data');
  }

  return response.json();
}

export async function logout() {
  setAuthToken(null);
}

// Card application endpoint
export async function applyForCard(request: ApplicationRequest): Promise<ApplicationResponse> {
  const response = await fetch(`${API_BASE_URL}/api/cards/apply`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    if (response.status === 401) {
      setAuthToken(null);
      throw new Error('Not authenticated');
    }
    const error = await response.json();
    throw new Error(error.detail || 'Application failed');
  }

  return response.json();
}


// Chat streaming functions

// Legionnaire chat streaming (basic concierge)
export async function* streamLegionnaireChatResponse(message: string, sessionId: string = 'default'): AsyncGenerator<ChatEvent> {
  const response = await fetch(`${API_BASE_URL}/api/chat/legionnaire/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message,
      session_id: sessionId,
    }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  if (!reader) {
    throw new Error('Response body is null');
  }

  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();

    if (done) {
      break;
    }

    buffer += decoder.decode(value, { stream: true });

    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const jsonStr = line.slice(6);
        try {
          const event: ChatEvent = JSON.parse(jsonStr);
          yield event;
        } catch (e) {
          console.error('Failed to parse SSE data:', e);
        }
      }
    }
  }
}

// Tribune chat streaming (premium with subagents)
export async function* streamChatResponse(message: string, sessionId: string = 'default'): AsyncGenerator<ChatEvent> {
  const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message,
      session_id: sessionId,
    }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  if (!reader) {
    throw new Error('Response body is null');
  }

  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();

    if (done) {
      break;
    }

    buffer += decoder.decode(value, { stream: true });

    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const jsonStr = line.slice(6);
        try {
          const event: ChatEvent = JSON.parse(jsonStr);
          yield event;
        } catch (e) {
          console.error('Failed to parse SSE data:', e);
        }
      }
    }
  }
}

// Accommodation endpoints
export async function getAccommodations(filters?: AccommodationFilters): Promise<Accommodation[]> {
  const queryParams = new URLSearchParams();

  if (filters?.country) {
    queryParams.append('country', filters.country);
  }
  if (filters?.type) {
    queryParams.append('type', filters.type);
  }
  if (filters?.minPrice !== undefined) {
    queryParams.append('min_price', filters.minPrice.toString());
  }
  if (filters?.maxPrice !== undefined) {
    queryParams.append('max_price', filters.maxPrice.toString());
  }
  if (filters?.minRating !== undefined) {
    queryParams.append('min_rating', filters.minRating.toString());
  }

  const url = `${API_BASE_URL}/api/accommodations${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;

  const response = await fetch(url, {
    headers: getHeaders(),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
}

export async function getAccommodationById(id: string): Promise<Accommodation> {
  const response = await fetch(`${API_BASE_URL}/api/accommodations/${id}`, {
    headers: getHeaders(),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
}

export async function bookAccommodation(request: BookingRequest): Promise<BookingResponse> {
  // Calculate nights from check-in and check-out dates
  const checkIn = new Date(request.checkInDate);
  const checkOut = new Date(request.checkOutDate);
  const nights = Math.max(1, Math.ceil((checkOut.getTime() - checkIn.getTime()) / (1000 * 60 * 60 * 24)));

  const response = await fetch(`${API_BASE_URL}/api/accommodations/book`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({
      accommodationId: request.accommodationId,
      paymentMethod: request.paymentMethod,
      nights,
      checkInDate: request.checkInDate,
      guests: request.guests,
    }),
  });

  if (!response.ok) {
    if (response.status === 401) {
      setAuthToken(null);
      throw new Error('Not authenticated');
    }
    const error = await response.json();
    throw new Error(error.detail || 'Booking failed');
  }

  return response.json();
}

// Experience endpoints
export async function getExperiences(filters?: {
  country?: string;
  type?: string;
  minPrice?: number;
  maxPrice?: number;
  minRating?: number;
}): Promise<Experience[]> {
  const queryParams = new URLSearchParams();

  if (filters?.country) {
    queryParams.append('country', filters.country);
  }
  if (filters?.type) {
    queryParams.append('type', filters.type);
  }
  if (filters?.minPrice !== undefined) {
    queryParams.append('min_price', filters.minPrice.toString());
  }
  if (filters?.maxPrice !== undefined) {
    queryParams.append('max_price', filters.maxPrice.toString());
  }
  if (filters?.minRating !== undefined) {
    queryParams.append('min_rating', filters.minRating.toString());
  }

  const url = `${API_BASE_URL}/api/travel/experiences${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;

  const response = await fetch(url, {
    headers: getHeaders(),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
}

export async function getExperienceById(id: string): Promise<Experience> {
  const response = await fetch(`${API_BASE_URL}/api/travel/experiences/${id}`, {
    headers: getHeaders(),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
}

export async function bookExperience(request: ExperienceBookingRequest): Promise<ExperienceBookingResponse> {
  // Transform the request to match backend's BookingRequest format
  const bookingRequest = {
    userId: request.userId,
    type: 'experience' as const,
    itemId: request.itemId,
    participants: request.participants,
    usePoints: request.paymentMethod === 'points',
    nights: null
  };

  const response = await fetch(`${API_BASE_URL}/api/travel/book`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(bookingRequest),
  });

  if (!response.ok) {
    if (response.status === 401) {
      setAuthToken(null);
      throw new Error('Not authenticated');
    }
    const error = await response.json();
    throw new Error(error.detail || 'Booking failed');
  }

  return response.json();
}

// Flights endpoints
export async function getFlights(): Promise<Flight[]> {
  const response = await fetch(`${API_BASE_URL}/api/flights`, {
    headers: getHeaders(),
  });

  if (!response.ok) {
    throw new Error('Failed to fetch flights');
  }

  return response.json();
}

export async function bookFlight(request: FlightBookingRequest): Promise<FlightBookingResponse> {
  const response = await fetch(`${API_BASE_URL}/api/flights/book`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    if (response.status === 401) {
      setAuthToken(null);
      throw new Error('Not authenticated');
    }
    const error = await response.json();
    throw new Error(error.detail || 'Booking failed');
  }

  return response.json();
}

// Restaurant endpoints
export async function getRestaurants(filters?: { country?: string; priceRange?: string[]; cuisine?: string; affordabilityTier?: string; searchQuery?: string }): Promise<Restaurant[]> {
  const queryParams = new URLSearchParams();

  if (filters?.country) {
    queryParams.append('country', filters.country);
  }
  if (filters?.priceRange && filters.priceRange.length > 0) {
    filters.priceRange.forEach(pr => queryParams.append('price_range', pr));
  }
  if (filters?.cuisine) {
    queryParams.append('cuisine', filters.cuisine);
  }
  if (filters?.affordabilityTier) {
    queryParams.append('affordability_tier', filters.affordabilityTier);
  }
  if (filters?.searchQuery) {
    queryParams.append('search', filters.searchQuery);
  }

  const url = `${API_BASE_URL}/api/travel/restaurants${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;

  const response = await fetch(url, {
    headers: getHeaders(),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
}

export async function getRestaurantById(id: string): Promise<Restaurant> {
  const response = await fetch(`${API_BASE_URL}/api/travel/restaurants/${id}`, {
    headers: getHeaders(),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
}

export async function makeRestaurantReservation(reservation: RestaurantReservation): Promise<{ success: boolean; message: string; reservation?: any }> {
  const response = await fetch(`${API_BASE_URL}/api/travel/restaurants/reserve`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(reservation),
  });

  if (!response.ok) {
    if (response.status === 401) {
      setAuthToken(null);
      throw new Error('Not authenticated');
    }
    const error = await response.json();
    throw new Error(error.detail || 'Reservation failed');
  }

  return response.json();
}
