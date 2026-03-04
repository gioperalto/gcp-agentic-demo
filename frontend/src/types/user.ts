export interface Address {
  street: string;
  city: string;
  state: string;
  zipCode: string;
  country: string;
}

export interface Reservation {
  id: string;
  type: 'accommodation' | 'restaurant' | 'flight' | 'experience';
  itemId: string;
  itemName: string;
  amount: number;
  date: string; // ISO 8601
  participants?: number;
  status: 'confirmed' | 'pending' | 'cancelled';
}

export interface User {
  id: string;
  username: string;
  firstName: string;
  lastName: string;
  email: string;
  birthDate: string; // YYYY-MM-DD
  salary: number;
  netWorth: number;
  creditScore: number;
  address: Address;
  currentCard: 'legionnaire' | 'tribune' | null;
  rejectionDate: string | null; // ISO 8601
  interestRate: number | null;
  creditLimit: number | null;
  availableCredit: number | null;
  rewardPoints: number;
  rewardPointsMultiplier: number | null;
  reservations: Reservation[];
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}
