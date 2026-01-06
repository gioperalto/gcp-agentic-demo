export interface Address {
  street: string;
  city: string;
  state: string;
  zipCode: string;
  country: string;
}

export interface User {
  id: string;
  username: string;
  email: string;
  birthDate: string; // YYYY-MM-DD
  salary: number;
  netWorth: number;
  creditScore: number;
  address: Address;
  currentCard: 'legionnaire' | 'tribune' | null;
  rejectionDate: string | null; // ISO 8601
  interestRate: number | null;
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
