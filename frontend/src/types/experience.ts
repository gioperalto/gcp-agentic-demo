export type ExperienceType =
  | 'hiking'
  | 'atv'
  | 'boat-ride'
  | 'yacht-ride'
  | 'winery-tour'
  | 'farm-to-table'
  | 'cultural'
  | 'adventure'
  | 'other';

export type AffordabilityTier = 'budget' | 'mid-range' | 'luxury';

export interface Experience {
  id: string;
  name: string;
  country: string;
  city: string;
  type: ExperienceType;
  price: number;
  duration: string;
  rating: number;
  imageUrl: string;
  description: string;
  minParticipants: number;
  maxParticipants: number;
  includedItems: string[];
  affordabilityTier: AffordabilityTier;
}

export interface ExperienceBookingRequest {
  userId: string;
  itemId: string;
  participants: number;
  date: string;
  paymentMethod: 'card' | 'points';
}

export interface ExperienceBookingResponse {
  success: boolean;
  message: string;
  reservation?: {
    id: string;
    type: 'experience';
    itemId: string;
    itemName: string;
    amount: number;
    date: string;
    participants: number;
    status: 'confirmed' | 'pending' | 'cancelled';
  };
  updatedUser?: {
    availableCredit: number;
    rewardPoints: number;
  };
}
