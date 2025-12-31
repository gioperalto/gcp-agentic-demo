import { getUserCardType } from '../utils/auth';
import './Account.css';

export const Account = () => {
  const cardType = getUserCardType();

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
      <div className="experience-header no-card-header">
        <h1>Discover Meridian Experiences</h1>
        <p>Apply for a card to unlock exclusive benefits</p>
      </div>

      <div className="application-section">
        <div className="application-card">
          <h2>Legionnaire Card</h2>
          <p className="card-tagline">Elevate your everyday experiences</p>
          <ul className="benefit-list">
            <li>3% rewards on all purchases</li>
            <li>Priority airport lounge access</li>
            <li>Exclusive dining experiences</li>
            <li>Travel insurance coverage</li>
            <li>24/7 concierge service</li>
          </ul>
          <div className="price">$495 annual fee</div>
          <button className="apply-card-button">Apply for Legionnaire</button>
        </div>

        <div className="application-card premium-card">
          <div className="premium-badge">PREMIUM</div>
          <h2>Tribune Card</h2>
          <p className="card-tagline">Experience luxury without limits</p>
          <ul className="benefit-list">
            <li>5% rewards on all purchases</li>
            <li>Private aviation access</li>
            <li>Luxury estate rentals</li>
            <li>Yacht charter services</li>
            <li>Dedicated personal concierge team</li>
            <li>Exclusive art and cultural experiences</li>
          </ul>
          <div className="price">$995 annual fee</div>
          <button className="apply-card-button premium">Apply for Tribune</button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="account-page">
      {cardType === 'legionnaire' && renderLegionnaireExperience()}
      {cardType === 'tribune' && renderTribuneExperience()}
      {cardType === 'none' && renderNoCardExperience()}
    </div>
  );
};
