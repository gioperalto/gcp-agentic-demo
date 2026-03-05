import { useNavigate } from 'react-router-dom';
import { getUserCardType, getCachedUser } from '../utils/auth';
import { CARDS } from '../data/cardData';
import './Account.css';

const QUICK_ACTIONS = [
  { label: 'Book Flights', path: '/flights', abbr: 'FL' },
  { label: 'Accommodations', path: '/accommodations', abbr: 'AC' },
  { label: 'Experiences', path: '/experiences', abbr: 'EX' },
  { label: 'Restaurants', path: '/restaurants', abbr: 'DN' },
  { label: 'Concierge', path: '/concierge', abbr: 'CG' },
  { label: 'Benefits', path: '/benefits', abbr: 'BN' },
];

export const Account = () => {
  const navigate = useNavigate();
  const cardType = getUserCardType();
  const user = getCachedUser();
  const currentCardData = CARDS.find(card => card.id === cardType);
  const isTribune = cardType === 'tribune';

  return (
    <div className="account-page">
      {user && currentCardData && (
        <>
          {/* Hero: Card image + user info side-by-side */}
          <section className={`acct-hero ${isTribune ? 'acct-hero--tribune' : ''}`}>
            <div className="acct-hero__card">
              <img
                src={currentCardData.imageUrl}
                alt={`${currentCardData.name} card`}
                className="acct-hero__card-img"
              />
              <div className="acct-hero__card-badge">
                {currentCardData.name}
              </div>
            </div>

            <div className="acct-hero__info">
              <p className="acct-hero__greeting">Welcome back,</p>
              <h1 className="acct-hero__name">{user.firstName} {user.lastName}</h1>
              <div className="acct-hero__meta">
                <span>{user.email}</span>
                <span className="acct-hero__sep" aria-hidden="true" />
                <span>@{user.username}</span>
              </div>

              <div className="acct-hero__stats">
                <div className="acct-stat">
                  <span className="acct-stat__value">{user.creditScore}</span>
                  <span className="acct-stat__label">Credit Score</span>
                </div>
                <div className="acct-stat">
                  <span className="acct-stat__value">{currentCardData.rewardsRate}</span>
                  <span className="acct-stat__label">Rewards Rate</span>
                </div>
                <div className="acct-stat">
                  <span className="acct-stat__value">${currentCardData.annualFee.toLocaleString()}</span>
                  <span className="acct-stat__label">Annual Fee</span>
                </div>
                <div className="acct-stat">
                  <span className="acct-stat__value">{user.interestRate ? `${user.interestRate}%` : 'N/A'}</span>
                  <span className="acct-stat__label">Interest Rate</span>
                </div>
              </div>
            </div>
          </section>

          {/* Details row */}
          <section className="acct-details">
            <div className="acct-details__block">
              <h3 className="acct-details__title">Address</h3>
              <p className="acct-details__text">
                {user.address.street}<br />
                {user.address.city}, {user.address.state} {user.address.zipCode}<br />
                {user.address.country}
              </p>
            </div>
            <div className="acct-details__block">
              <h3 className="acct-details__title">Card Benefits</h3>
              <ul className="acct-details__benefits">
                {currentCardData.benefits.map((b, i) => (
                  <li key={i}>{b}</li>
                ))}
              </ul>
            </div>
            <div className="acct-details__block acct-details__block--cta">
              <button className="acct-details__btn" onClick={() => navigate('/benefits')}>
                View All Benefits
              </button>
            </div>
          </section>

          {/* Quick actions */}
          <section className="acct-actions">
            <h2 className="acct-actions__title">Quick Actions</h2>
            <div className="acct-actions__grid">
              {QUICK_ACTIONS.map(action => (
                <button
                  key={action.path}
                  className={`acct-action ${isTribune ? 'acct-action--tribune' : ''}`}
                  onClick={() => navigate(action.path)}
                >
                  <span className="acct-action__icon">{action.abbr}</span>
                  <span className="acct-action__label">{action.label}</span>
                </button>
              ))}
            </div>
          </section>
        </>
      )}

      {cardType === 'none' && (
        <section className="acct-no-card">
          <h1 className="acct-no-card__title">Unlock the benefits of Meridian</h1>
          <p className="acct-no-card__sub">Apply for a card to access cashback rewards, concierge services, and more.</p>
          <div className="acct-no-card__cards">
            {CARDS.map((card) => (
              <div key={card.id} className={`acct-no-card__option ${card.id === 'tribune' ? 'acct-no-card__option--tribune' : ''}`}>
                <img src={card.imageUrl} alt={card.name} className="acct-no-card__img" />
                <h2 className="acct-no-card__name">{card.name}</h2>
                <p className="acct-no-card__fee">${card.annualFee.toLocaleString()} / year</p>
                <button
                  className={`acct-no-card__apply ${card.id === 'tribune' ? 'acct-no-card__apply--tribune' : ''}`}
                  onClick={() => navigate(`/apply?card=${card.slug}`)}
                >
                  Apply Now
                </button>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
};
