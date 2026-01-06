import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import type { CreditCard, ApprovalStatus, ApprovalFormData } from '../types/cards';
import './CardModal.css';

interface CardModalProps {
  isOpen: boolean;
  onClose: () => void;
  card: CreditCard | null;
}

export const CardModal = ({ isOpen, onClose, card }: CardModalProps) => {
  const navigate = useNavigate();
  const [showApprovalForm, setShowApprovalForm] = useState(false);
  const [formData, setFormData] = useState<ApprovalFormData>({
    salary: '',
    netWorth: '',
    age: '',
    ficoScore: ''
  });
  const [approvalStatus, setApprovalStatus] = useState<ApprovalStatus | null>(null);
  const [formSubmitted, setFormSubmitted] = useState(false);
  const [formErrors, setFormErrors] = useState<{ [key: string]: string }>({});

  // Handle Escape key to close modal
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        handleClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden'; // Prevent body scroll
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  const handleClose = () => {
    // Reset form state when closing
    setShowApprovalForm(false);
    setFormData({ salary: '', netWorth: '', age: '', ficoScore: '' });
    setApprovalStatus(null);
    setFormSubmitted(false);
    setFormErrors({});
    onClose();
  };

  const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      handleClose();
    }
  };

  const validateForm = (): boolean => {
    const errors: { [key: string]: string } = {};

    const salary = parseFloat(formData.salary);
    const netWorth = parseFloat(formData.netWorth);
    const age = parseInt(formData.age);
    const fico = parseInt(formData.ficoScore);

    if (!formData.salary || isNaN(salary) || salary <= 0) {
      errors.salary = 'Please enter a valid salary greater than 0';
    }

    if (!formData.netWorth || isNaN(netWorth) || netWorth < 0) {
      errors.netWorth = 'Please enter a valid net worth of 0 or more';
    }

    if (!formData.age || isNaN(age) || age < 18 || age > 120) {
      errors.age = 'Please enter an age between 18 and 120';
    }

    if (!formData.ficoScore || isNaN(fico) || fico < 300 || fico > 850) {
      errors.ficoScore = 'Please enter a FICO score between 300 and 850';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const calculateApprovalStatus = (): ApprovalStatus => {
    if (!card) return 'Unlikely';

    const salary = parseFloat(formData.salary);
    const netWorth = parseFloat(formData.netWorth); 
    const age = parseInt(formData.age);
    const fico = parseInt(formData.ficoScore);

    const { approvalThresholds } = card;

    // Check highly qualified (all criteria must be met)
    if (
      salary >= approvalThresholds.highlyQualified.minSalary &&
      netWorth >= approvalThresholds.highlyQualified.minNetWorth &&
      age >= approvalThresholds.highlyQualified.minAge &&
      fico >= approvalThresholds.highlyQualified.minFico
    ) {
      return 'Highly Qualified';
    }

    // Check likely (all criteria must be met)
    if (
      salary >= approvalThresholds.likely.minSalary &&
      netWorth >= approvalThresholds.likely.minNetWorth &&
      age >= approvalThresholds.likely.minAge &&
      fico >= approvalThresholds.likely.minFico
    ) {
      return 'Likely';
    }

    return 'Unlikely';
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (validateForm()) {
      const status = calculateApprovalStatus();
      setApprovalStatus(status);
      setFormSubmitted(true);
    }
  };

  const handleInputChange = (field: keyof ApprovalFormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error for this field when user starts typing
    if (formErrors[field]) {
      setFormErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const renderStars = (rating: number) => {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    const stars = [];

    for (let i = 0; i < fullStars; i++) {
      stars.push(<span key={`full-${i}`} className="star full">★</span>);
    }
    if (hasHalfStar) {
      stars.push(<span key="half" className="star half">★</span>);
    }
    const emptyStars = 5 - stars.length;
    for (let i = 0; i < emptyStars; i++) {
      stars.push(<span key={`empty-${i}`} className="star empty">☆</span>);
    }

    return stars;
  };

  if (!isOpen || !card) return null;

  return (
    <div className="card-modal-overlay" onClick={handleBackdropClick}>
      <div className={`card-modal-container ${card.slug}`}>
        <button className="modal-close-button" onClick={handleClose} aria-label="Close">
          ✕
        </button>

        <div className="modal-card-image">
          <img src={card.imageUrl} alt={`${card.name} card`} />
        </div>

        <h2 className="modal-card-name">{card.name}</h2>

        <div className="modal-info-row">
          <div className="info-section credit-section">
            <div className="info-label">FICO Score Average</div>
            <div className="info-value">{card.averageCreditScore}</div>
          </div>
          <div className="info-section reviews-section">
            <div className="info-label">Customer Reviews</div>
            <div className="stars-container">
              {renderStars(card.starRating)}
              <span className="rating-text">{card.starRating}</span>
            </div>
            <div className="review-count">{card.reviewCount.toLocaleString()} reviews</div>
          </div>
        </div>

        <div className="modal-story-section">
          <h3>About this Card</h3>
          <p>{card.story}</p>
        </div>

        <div className="modal-details-section">
          <div className="detail-row">
            <span className="detail-label">Annual Fee:</span>
            <span className="detail-value">${card.annualFee.toLocaleString()}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">APR Range:</span>
            <span className="detail-value">{card.aprRange}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Rewards Rate:</span>
            <span className="detail-value">{card.rewardsRate}</span>
          </div>
        </div>

        <div className="modal-actions">
          <button
            className="check-approval-button"
            onClick={() => setShowApprovalForm(!showApprovalForm)}
          >
            {showApprovalForm ? 'Hide Approval Form' : 'See if I\'m Approved'}
          </button>

          {showApprovalForm && (
            <form className="approval-form" onSubmit={handleFormSubmit}>
              <div className="form-group">
                <label htmlFor="salary">Annual Salary ($)</label>
                <input
                  type="number"
                  id="salary"
                  value={formData.salary}
                  onChange={(e) => handleInputChange('salary', e.target.value)}
                  placeholder="e.g. $75,000"
                  className={formErrors.salary ? 'error' : ''}
                />
                {formErrors.salary && <span className="error-message">{formErrors.salary}</span>}
              </div>

              <div className="form-group">
                <label htmlFor="netWorth">Net Worth ($)</label>
                <input
                  type="number"
                  id="netWorth"
                  value={formData.netWorth}
                  onChange={(e) => handleInputChange('netWorth', e.target.value)}
                  placeholder="e.g. $100,000"
                  className={formErrors.netWorth ? 'error' : ''}
                />
                {formErrors.netWorth && <span className="error-message">{formErrors.netWorth}</span>}
              </div>

              <div className="form-group">
                <label htmlFor="age">Age</label>
                <input
                  type="number"
                  id="age"
                  value={formData.age}
                  onChange={(e) => handleInputChange('age', e.target.value)}
                  placeholder="e.g., 30"
                  className={formErrors.age ? 'error' : ''}
                />
                {formErrors.age && <span className="error-message">{formErrors.age}</span>}
              </div>

              <div className="form-group">
                <label htmlFor="ficoScore">FICO Score</label>
                <input
                  type="number"
                  id="ficoScore"
                  value={formData.ficoScore}
                  onChange={(e) => handleInputChange('ficoScore', e.target.value)}
                  placeholder="e.g., 750"
                  className={formErrors.ficoScore ? 'error' : ''}
                />
                {formErrors.ficoScore && <span className="error-message">{formErrors.ficoScore}</span>}
              </div>

              <button type="submit" className="submit-approval-button">
                Check My Approval Odds
              </button>
            </form>
          )}

          {formSubmitted && approvalStatus && (
            <div className={`approval-status ${approvalStatus.toLowerCase().replace(' ', '-')}`}>
              <h4>Approval Status: {approvalStatus}</h4>
              <p>
                {approvalStatus === 'Highly Qualified' &&
                  'Congratulations! You exceed all requirements for this card. You have excellent approval odds.'}
                {approvalStatus === 'Likely' &&
                  'You meet the basic requirements for this card. You have good approval odds.'}
                {approvalStatus === 'Unlikely' &&
                  'Based on the information provided, approval may be challenging. Consider improving your financial profile or exploring other card options.'}
              </p>
            </div>
          )}

          <button
            className="apply-now-button"
            onClick={() => {
              if (card) {
                navigate(`/apply?card=${card.slug}`);
              }
            }}
          >
            Apply Now
          </button>
        </div>
      </div>
    </div>
  );
};
