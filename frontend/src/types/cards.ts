export interface ApprovalThresholds {
  highlyQualified: {
    minSalary: number;
    minNetWorth: number;
    minAge: number;
    minFico: number;
  };
  likely: {
    minSalary: number;
    minNetWorth: number;
    minAge: number;
    minFico: number;
  };
}

export interface CreditCard {
  id: string;
  name: string;
  slug: 'legionnaire' | 'tribune';
  annualFee: number;
  aprRange: string;
  averageCreditScore: number;
  rewardsRate: string;
  benefits: string[];
  story: string;
  imageUrl: string;
  starRating: number;
  reviewCount: number;
  approvalThresholds: ApprovalThresholds;
}

export type ApprovalStatus = 'Unlikely' | 'Likely' | 'Highly Qualified';

export interface ApprovalFormData {
  salary: string;
  netWorth: string;
  age: string;
  ficoScore: string;
}
