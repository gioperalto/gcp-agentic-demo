import { useNavigate } from 'react-router-dom';
import { getUserCardType, getCachedUser } from '../utils/auth';
import { CARDS } from '../data/cardData';
import './Account.css';

export const Account = () => {
  const navigate = useNavigate();
  const cardType = getUserCardType();
  const user = getCachedUser();
  const currentCardData = CARDS.find(card => card.id === cardType);

  const renderPersonalInfo = () => {
    if (!user) return null;

    return (
      <div className="membership-stats-section">
        <h2>Personal Information</h2>
        <div className="stats-grid">
          <div className="stat-item">
            <div className="stat-number">User Info</div>
            <div className="stat-description white">{user.username}</div>
            <div className="stat-description white">{user.email}</div>
          </div>
          <div className="stat-item">
            <div className="stat-number">{user.creditScore}</div>
            <div className="stat-description white">Credit Score</div>
          </div>
          <div className="stat-item">
            <div className="stat-number">Address</div>
            <div className="stat-description white">
              {user.address.street}<br />
              {user.address.city}, {user.address.state} {user.address.zipCode}<br />
              {user.address.country}
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderCardDetails = () => {
    if (!user || !currentCardData) return null;

    return (
      <div className="card-details-section">
        <h2>Your {currentCardData.name} Card</h2>
        <div className="card-details-grid">
          <div className="card-detail-item">
            <div className="detail-icon">💳</div>
            <div className="detail-content">
              <div className="detail-label">Card Type</div>
              <div className="detail-value">{currentCardData.name}</div>
            </div>
          </div>
          <div className="card-detail-item">
            <div className="detail-icon">%</div>
            <div className="detail-content">
              <div className="detail-label">Interest Rate</div>
              <div className="detail-value">{user.interestRate ? `${user.interestRate}%` : 'N/A'}</div>
            </div>
          </div>
          <div className="card-detail-item">
            <div className="detail-icon">💵</div>
            <div className="detail-content">
              <div className="detail-label">Annual Fee</div>
              <div className="detail-value">${currentCardData.annualFee}</div>
            </div>
          </div>
          <div className="card-detail-item">
            <div className="detail-icon">🎁</div>
            <div className="detail-content">
              <div className="detail-label">Rewards Rate</div>
              <div className="detail-value">{currentCardData.rewardsRate}</div>
            </div>
          </div>
        </div>
        <div className="card-benefits-summary">
          <h3>Your Benefits</h3>
          <ul>
            {currentCardData.benefits.map((benefit, index) => (
              <li key={index}>{benefit}</li>
            ))}
          </ul>
          <button className="view-benefits-button" onClick={() => window.location.href = '/benefits'}>
            View All Benefits
          </button>
        </div>
      </div>
    );
  };

  const renderLegionnaireExperience = () => (
    <div className="experience-content">
      <div className="experience-header legionnaire-header">
        <h1>Welcome, Legionnaire Cardholder</h1>
        <p>Your exclusive benefits and experiences await</p>
      </div>

      <div className="experiences-grid">
        <div className="experience-card">
          <div className="experience-icon">✈️</div>
          <h3>Priority Lounge Access</h3>
          <p>Access over 1,000 airport lounges worldwide with complimentary food, drinks, and Wi-Fi.</p>
          <button className="book-button">Book Now</button>
        </div>

        <div className="experience-card">
          <div className="experience-icon">🍽️</div>
          <h3>Exclusive Dining</h3>
          <p>Reserved tables at Michelin-starred restaurants and exclusive culinary events.</p>
          <button className="book-button">View Restaurants</button>
        </div>

        <div className="experience-card">
          <div className="experience-icon">🎭</div>
          <h3>VIP Events</h3>
          <p>Front-row seats to concerts, theater premieres, and exclusive member gatherings.</p>
          <button className="book-button">See Events</button>
        </div>

        <div className="experience-card">
          <div className="experience-icon">🏨</div>
          <h3>Hotel Upgrades</h3>
          <p>Complimentary room upgrades and late checkout at partner luxury hotels worldwide.</p>
          <button className="book-button">Explore Hotels</button>
        </div>

        <div className="experience-card">
          <div className="experience-icon">🚗</div>
          <h3>Luxury Car Rental</h3>
          <p>Premium car rental discounts and complimentary upgrades from our partners.</p>
          <button className="book-button">Rent Now</button>
        </div>

        <div className="experience-card">
          <div className="experience-icon">📞</div>
          <h3>24/7 Concierge</h3>
          <p>Personal concierge service for travel bookings, reservations, and special requests.</p>
          <button className="book-button">Contact Concierge</button>
        </div>
      </div>
    </div>
  );

  const renderTribuneExperience = () => (
    <div className="experience-content">
      <div className="experience-header tribune-header">
        <h1>Welcome, Tribune Cardholder</h1>
        <p>Experience the pinnacle of luxury and exclusivity</p>
      </div>

      <div className="experiences-grid">
        <div className="experience-card premium">
          <div className="experience-icon">🛩️</div>
          <h3>Private Aviation</h3>
          <p>Access to private jet charters and helicopter services with preferential rates.</p>
          <button className="book-button premium">Book Flight</button>
        </div>

        <div className="experience-card premium">
          <div className="experience-icon">🏰</div>
          <h3>Luxury Estates</h3>
          <p>Exclusive access to private villas, penthouses, and luxury estates worldwide.</p>
          <button className="book-button premium">View Properties</button>
        </div>

        <div className="experience-card premium">
          <div className="experience-icon">🎨</div>
          <h3>Art & Culture</h3>
          <p>Private museum tours, art gallery previews, and exclusive auction access.</p>
          <button className="book-button premium">Explore Culture</button>
        </div>

        <div className="experience-card premium">
          <div className="experience-icon">⛵</div>
          <h3>Yacht Experiences</h3>
          <p>Charter luxury yachts for private excursions in the world's most beautiful waters.</p>
          <button className="book-button premium">Charter Yacht</button>
        </div>

        <div className="experience-card premium">
          <div className="experience-icon">🍾</div>
          <h3>Wine & Spirits</h3>
          <p>Private wine cellar access, rare spirit tastings, and vineyard tours.</p>
          <button className="book-button premium">Discover Wines</button>
        </div>

        <div className="experience-card premium">
          <div className="experience-icon">👔</div>
          <h3>Personal Shopper</h3>
          <p>Dedicated personal shopping services at luxury boutiques and fashion houses.</p>
          <button className="book-button premium">Schedule Appointment</button>
        </div>

        <div className="experience-card premium">
          <div className="experience-icon">🏌️</div>
          <h3>Elite Sports Access</h3>
          <p>VIP access to major sporting events, golf courses, and exclusive sporting clubs.</p>
          <button className="book-button premium">View Events</button>
        </div>

        <div className="experience-card premium">
          <div className="experience-icon">💎</div>
          <h3>Dedicated Concierge</h3>
          <p>Your personal concierge team available 24/7 for any request, anywhere in the world.</p>
          <button className="book-button premium">Contact Team</button>
        </div>
      </div>
    </div>
  );

  const renderNoCardExperience = () => (
    <div className="experience-content">
      <div className="experience-header">
        <h1>Unlock the benefits of Meridian</h1>
        <p>Apply for a card to gain access to cashback rewards, concierge services, and more.</p>
      </div>

      <div className="cards-container">
        {CARDS.map((card) => (
          <div key={card.id} className={`credit-card ${card.slug}`}>
            <div className="card-image-placeholder">
              <div className="image-credit">
                Generated with Nano Banana
                <span className="credit-icon">🍌</span>
              </div>
            </div>
            <div className="card-info">
              <h2 className="card-name">{card.name}</h2>
              <div className="card-details">
                <div className="card-detail-item">
                  <span className="detail-label">Annual Fee:</span>
                  <span className="detail-value">${card.annualFee}</span>
                </div>
                <div className="card-detail-item">
                  <span className="detail-label">APR range:</span>
                  <span className="detail-value">{card.aprRange}</span>
                </div>
                <div className="card-detail-item">
                  <span className="detail-label">Average credit score:</span>
                  <span className="detail-value">{card.averageCreditScore}</span>
                </div>
                <div className="card-detail-item">
                  <span className="detail-label">Rewards Rate:</span>
                  <span className="detail-value">{card.rewardsRate}</span>
                </div>
              </div>
              <div className="card-benefits">
                <h3>{card.id === 'tribune' ? 'Additional Benefits:' : 'Benefits:'}</h3>
                <ul>
                  {card.benefits.map((benefit, index) => (
                    <li key={index}>{benefit}</li>
                  ))}
                </ul>
              </div>
              <div className="card-actions">
                <button
                  className={`apply-button ${card.slug === 'tribune' ? 'premium' : ''}` }
                  onClick={() => navigate(`/apply?card=${card.slug}`)}
                >
                  Apply Now
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="account-page">
      {user && (
        <>
          {renderPersonalInfo()}
          {renderCardDetails()}
        </>
      )}
      {cardType === 'legionnaire' && renderLegionnaireExperience()}
      {cardType === 'tribune' && renderTribuneExperience()}
      {cardType === 'none' && renderNoCardExperience()}
    </div>
  );
};
