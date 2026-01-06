export interface ApplicationRequest {
  cardSlug: 'legionnaire' | 'tribune';
}

export interface ApplicationResponse {
  success: boolean;
  status: 'approved' | 'rejected';
  approvalTier: 'Highly Qualified' | 'Likely' | 'Unlikely';
  interestRate: number | null;
  message: string;
  rejectionDate: string | null;
}
