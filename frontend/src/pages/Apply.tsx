import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { CARDS } from '../data/cardData';
import type { CreditCard, ApprovalStatus } from '../types/cards';
import type { User } from '../types/user';
import type { ApplicationResponse } from '../types/application';
import { applyForCard } from '../utils/api';
import { fetchCurrentUser } from '../utils/auth';
import './Apply.css';

export const Apply = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const cardSlug = searchParams.get('card') as 'legionnaire' | 'tribune' | null;

  const [card, setCard] = useState<CreditCard | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [applying, setApplying] = useState(false);
  const [result, setResult] = useState<ApplicationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Load card and user data
    const loadData = async () => {
      setLoading(true);
      setError(null);

      // Find card
      if (!cardSlug) {
        setError('No card specified');
        setLoading(false);
        return;
      }

      const foundCard = CARDS.find(c => c.slug === cardSlug);
      if (!foundCard) {
        setError('Card not found');
        setLoading(false);
        return;
      }
      setCard(foundCard);

      // Fetch user data
      try {
        const userData = await fetchCurrentUser();
        if (!userData) {
          setError('Please log in to apply for a card');
          setLoading(false);
          return;
        }
        setUser(userData);
      } catch (err) {
        setError('Failed to load user data. Please log in.');
      }

      setLoading(false);
    };

    loadData();
  }, [cardSlug]);

  const calculateAge = (birthDate: string): number => {
    const birth = new Date(birthDate);
    const today = new Date();
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--;
    }
    return age;
  };

  const calculateApprovalStatus = (): ApprovalStatus => {
    if (!card || !user) return 'Unlikely';

    const age = calculateAge(user.birthDate);
    const { approvalThresholds } = card;

    // Check highly qualified
    if (
      user.salary >= approvalThresholds.highlyQualified.minSalary &&
      user.netWorth >= approvalThresholds.highlyQualified.minNetWorth &&
      age >= approvalThresholds.highlyQualified.minAge &&
      user.creditScore >= approvalThresholds.highlyQualified.minFico
    ) {
      return 'Highly Qualified';
    }

    // Check likely
    if (
      user.salary >= approvalThresholds.likely.minSalary &&
      user.netWorth >= approvalThresholds.likely.minNetWorth &&
      age >= approvalThresholds.likely.minAge &&
      user.creditScore >= approvalThresholds.likely.minFico
    ) {
      return 'Likely';
    }

    return 'Unlikely';
  };

  const handleApply = async () => {
    if (!card || !user) return;

    setApplying(true);
    setError(null);

    try {
      const response = await applyForCard({ cardSlug: card.slug });
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Application failed');
    } finally {
      setApplying(false);
    }
  };

  if (loading) {
    return (
      <div className="apply-page">
        <div className="loading">Loading...</div>
      </div>
    );
  }

  if (error && !card) {
    return (
      <div className="apply-page">
        <div className="error-message">{error}</div>
        <button onClick={() => navigate('/cards')} className="back-button">
          Back to Cards
        </button>
      </div>
    );
  }

  if (!card || !user) {
    return (
      <div className="apply-page">
        <div className="error-message">Unable to load application</div>
        <button onClick={() => navigate('/cards')} className="back-button">
          Back to Cards
        </button>
      </div>
    );
  }

  const approvalStatus = calculateApprovalStatus();

  return (
    <div className="apply-page">
      <div className="apply-container">
        <h1>Apply for {card.name}</h1>

        <div className="card-preview">
          <img src={card.imageUrl} alt={`${card.name} card`} />
          <div className="card-details">
            <h3>{card.name}</h3>
            <p className="card-fee">Annual Fee: ${card.annualFee.toLocaleString()}</p>
            <p className="card-apr">APR Range: {card.aprRange}</p>
            <p className="card-rewards">Rewards: {card.rewardsRate}</p>
          </div>
        </div>

        {!result && (
          <>
            <div className="approval-preview">
              <h3>Your Approval Odds</h3>
              <div className={`approval-indicator ${approvalStatus.toLowerCase().replace(' ', '-')}`}>
                {approvalStatus}
              </div>
              <p className="approval-description">
                {approvalStatus === 'Highly Qualified' &&
                  'You exceed all requirements for this card. You have excellent approval odds.'}
                {approvalStatus === 'Likely' &&
                  'You meet the basic requirements for this card. You have good approval odds.'}
                {approvalStatus === 'Unlikely' &&
                  'Based on your profile, approval may be challenging. If rejected, you will need to wait 60 days before applying again.'}
              </p>
            </div>

            <div className="user-info">
              <h3>Application Information</h3>
              <div className="info-grid">
                <div className="info-item">
                  <span className="info-label">Annual Salary:</span>
                  <span className="info-value">${user.salary.toLocaleString()}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Net Worth:</span>
                  <span className="info-value">${user.netWorth.toLocaleString()}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Credit Score:</span>
                  <span className="info-value">{user.creditScore}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Age:</span>
                  <span className="info-value">{calculateAge(user.birthDate)}</span>
                </div>
              </div>
            </div>

            {error && <div className="error-message">{error}</div>}

            <div className="apply-actions">
              <button
                onClick={handleApply}
                disabled={applying}
                className="submit-application-button"
              >
                {applying ? 'Processing...' : 'Submit Application'}
              </button>
              <button
                onClick={() => user ? navigate('/account') : navigate('/cards')}
                className="cancel-button"
                disabled={applying}
              >
                Cancel
              </button>
            </div>
          </>
        )}

        {result && (
          <div className="application-result">
            <div className={`result-header ${result.status}`}>
              <h2>{result.status === 'approved' ? 'Congratulations!' : 'Application Rejected'}</h2>
            </div>

            <div className="result-details">
              <p className="result-message">{result.message}</p>

              {result.status === 'approved' && result.interestRate && (
                <div className="approval-details">
                  <div className="detail-item">
                    <span className="detail-label">Approval Tier:</span>
                    <span className="detail-value">{result.approvalTier}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Your APR:</span>
                    <span className="detail-value">{result.interestRate}%</span>
                  </div>
                  <p className="next-steps">
                    Your card will arrive in 7-10 business days. You can view your account details in the Account section.
                  </p>
                </div>
              )}

              {result.status === 'rejected' && result.rejectionDate && (
                <div className="rejection-details">
                  <p className="waiting-period">
                    You may apply again after 60 days from your rejection date.
                  </p>
                </div>
              )}
            </div>

            <div className="result-actions">
              <button
                onClick={() => navigate('/account')}
                className="view-account-button"
              >
                {result.status === 'approved' ? 'View Account' : 'Back to Account'}
              </button>
              <button
                onClick={() => navigate('/cards')}
                className="view-cards-button"
              >
                View All Cards
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
