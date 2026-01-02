import type { CreditCard } from '../types/cards';

export const CARDS: CreditCard[] = [
  {
    id: 'legionnaire',
    name: 'Legionnaire',
    slug: 'legionnaire',
    annualFee: 120,
    aprRange: '12.99% - 24.99%',
    averageCreditScore: 720,
    rewardsRate: '2% on all purchases',
    benefits: [
      'Travel insurance coverage',
      '24/7 concierge chat'
    ],
    story: 'The Legionnaire card provides the look and feel of luxury without the price tag. With a low annual fee, and a competitive return on all purchases, it\'s the perfect everyday card for just about anybody.',
    imageUrl: '/img/cards/legionnaire.png',
    starRating: 4.7,
    reviewCount: 2547,
    approvalThresholds: {
      highlyQualified: {
        minSalary: 75000,
        minNetWorth: 0,
        minAge: 25,
        minFico: 720
      },
      likely: {
        minSalary: 50000,
        minNetWorth: 0,
        minAge: 21,
        minFico: 700
      }
    }
  },
  {
    id: 'tribune',
    name: 'Tribune',
    slug: 'tribune',
    annualFee: 10000,
    aprRange: '4.99-9.99%',
    averageCreditScore: 820,
    rewardsRate: 'Up to 5% on select purchases*',
    benefits: [
      'Complimentary Tribune lounge access worldwide',
      'Dedicated personal concierge',
      'Access to Tribune dining experiences',
      'Access to Tribune private jet share'
    ],
    story: `The Tribune card represents the pinnacle of luxury and exclusivity. Reserved for high-net-worth individuals who demand nothing but the best, this is more than just a credit card. It\'s a lifestyle.`,
    imageUrl: '/img/cards/tribune.png',
    starRating: 4.9,
    reviewCount: 1203,
    approvalThresholds: {
      highlyQualified: {
        minSalary: 200000,
        minNetWorth: 1000000,
        minAge: 30,
        minFico: 800
      },
      likely: {
        minSalary: 150000,
        minNetWorth: 800000,
        minAge: 25,
        minFico: 750
      }
    }
  }
];
