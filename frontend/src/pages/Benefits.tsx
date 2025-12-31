import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import './Benefits.css';

export const Benefits = () => {
  const [activeSection, setActiveSection] = useState('');
  const location = useLocation();

  useEffect(() => {
    // Handle hash navigation from URL
    if (location.hash) {
      const sectionId = location.hash.substring(1); // Remove the # symbol
      setTimeout(() => {
        const element = document.getElementById(sectionId);
        if (element) {
          element.scrollIntoView({ behavior: 'smooth', block: 'start' });
          setActiveSection(sectionId);
        }
      }, 100); // Small delay to ensure the page is fully rendered
    }
  }, [location]);

  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
      setActiveSection(sectionId);
    }
  };

  return (
    <div className="benefits-page">
      <div className="benefits-header">
        <h1>Exclusive Benefits</h1>
        <p>Experience premium perks designed for your lifestyle</p>
      </div>

      <div className="benefits-navigation">
        <button
          className={`nav-pill ${activeSection === 'travel-insurance' ? 'active' : ''}`}
          onClick={() => scrollToSection('travel-insurance')}
        >
          Travel Insurance
        </button>
        <button
          className={`nav-pill ${activeSection === 'concierge' ? 'active' : ''}`}
          onClick={() => scrollToSection('concierge')}
        >
          Concierge Services
        </button>
        <button
          className={`nav-pill ${activeSection === 'lounge' ? 'active' : ''}`}
          onClick={() => scrollToSection('lounge')}
        >
          Tribune Lounge
        </button>
        <button
          className={`nav-pill ${activeSection === 'dining' ? 'active' : ''}`}
          onClick={() => scrollToSection('dining')}
        >
          Tribune Dining
        </button>
        <button
          className={`nav-pill ${activeSection === 'jet-share' ? 'active' : ''}`}
          onClick={() => scrollToSection('jet-share')}
        >
          Tribune Private Jet
        </button>
      </div>

      <div className="benefits-content">
        <section id="travel-insurance" className="benefit-section">
          <div className="section-icon">✈️</div>
          <h2>Travel Insurance</h2>
          <div className="section-description">
            <p>
              Travel with peace of mind knowing you're protected by comprehensive insurance coverage.
              All Meridian cardholders enjoy automatic travel insurance benefits when booking trips with their card.
            </p>
          </div>
          <div className="benefit-features">
            <div className="feature-card">
              <h3>Trip Cancellation & Interruption</h3>
              <p>Coverage up to $10,000 per trip for unexpected cancellations or interruptions due to covered reasons.</p>
            </div>
            <div className="feature-card">
              <h3>Baggage Delay & Loss</h3>
              <p>Reimbursement for essential purchases if your baggage is delayed more than 6 hours or permanently lost.</p>
            </div>
            <div className="feature-card">
              <h3>Emergency Medical Coverage</h3>
              <p>Up to $50,000 in emergency medical and dental coverage when traveling outside your home country.</p>
            </div>
          </div>
          <p className="benefit-note">Available to all Legionnaire and Tribune cardholders</p>
        </section>

        <section id="concierge" className="benefit-section">
          <div className="section-icon">💬</div>
          <h2>Concierge Services</h2>
          <div className="section-description">
            <p>
              Access dedicated support tailored to your needs, from everyday requests to extraordinary experiences.
              Our concierge services adapt to your card tier, providing the perfect level of personalized assistance.
            </p>
          </div>

          <div className="concierge-tiers">
            <div className="tier-card legionnaire-tier">
              <h3>Legionnaire Concierge</h3>
              <div className="tier-badge">Chat Services</div>
              <p className="tier-description">
                Connect instantly with our professional concierge team through 24/7 chat support.
                Get assistance with reservations, travel planning, event tickets, and personalized recommendations.
              </p>
              <ul className="tier-features">
                <li>24/7 chat-based concierge support</li>
                <li>Restaurant reservations and recommendations</li>
                <li>Event and entertainment booking</li>
                <li>Travel planning assistance</li>
                <li>Gift recommendations and ordering</li>
              </ul>
            </div>

            <div className="tier-card tribune-tier">
              <h3>Tribune AI Concierge Team</h3>
              <div className="tier-badge premium">Cutting-Edge AI Team</div>
              <p className="tier-description">
                Experience the future of personalized service with our elite AI concierge team.
                Choose to chat or speak with specialized AI agents trained to anticipate your needs and deliver
                exceptional service across every aspect of your lifestyle.
              </p>
              <ul className="tier-features">
                <li>24/7 AI-powered chat and voice concierge</li>
                <li>Multi-agent team specialized by expertise</li>
                <li>Proactive suggestions based on preferences</li>
                <li>Exclusive access to sold-out events</li>
                <li>Complex multi-destination travel planning</li>
                <li>Private event coordination and planning</li>
                <li>Personal shopping and styling services</li>
                <li>VIP experiences and behind-the-scenes access</li>
              </ul>
              <p className="tribune-exclusive">Exclusive to Tribune cardholders</p>
            </div>
          </div>
        </section>

        <section id="lounge" className="benefit-section tribune-only">
          <div className="section-icon">✨</div>
          <div className="tribune-badge">Tribune Exclusive</div>
          <h2>Tribune Lounge</h2>
          <div className="section-description">
            <p>
              Escape the chaos of the terminal and relax in our premium airport lounges stationed across the country.
              Enjoy exceptional comfort, complimentary amenities, and personalized service pre-flight.
            </p>
          </div>
          <div className="benefit-features">
            <div className="feature-card">
              <h3>Premium Comfort & Amenities</h3>
              <p>
                Unwind in spacious seating areas with gourmet food, premium beverages,
                high-speed WiFi, and shower facilities. Every lounge features a curated selection of
                refreshments and comfortable workspaces.
              </p>
            </div>
            <div className="feature-card">
              <h3>Nationwide Access</h3>
              <p>
                Access to multiple Tribune Lounges at major airports across the United States.
                Complimentary access for you and up to two guests per visit, ensuring your
                entire party travels in style.
              </p>
            </div>
            <div className="feature-card">
              <h3>Personalized Service</h3>
              <p>
                Dedicated lounge staff ready to assist you. Enjoy priority boarding notifications 
                and a seamless transition to your gate.
              </p>
            </div>
          </div>
          <p className="tribune-exclusive">This premium benefit is exclusively available to Tribune cardholders</p>
        </section>

        <section id="dining" className="benefit-section tribune-only">
          <div className="section-icon">🍽️</div>
          <div className="tribune-badge">Tribune Exclusive</div>
          <h2>Tribune Dining</h2>
          <div className="section-description">
            <p>
              Elevate your culinary experiences with exclusive access to the world's most sought-after restaurants
              and intimate dining experiences crafted for Tribune cardholders.
            </p>
          </div>
          <div className="benefit-features">
            <div className="feature-card">
              <h3>Priority Reservations</h3>
              <p>
                Skip the waitlist at Michelin-starred restaurants and exclusive dining establishments worldwide.
                Our concierge team secures reservations at some of the most elite restaurants.
              </p>
            </div>
            <div className="feature-card">
              <h3>Private Chef Experiences</h3>
              <p>
                Arrange intimate dinners with world-renowned chefs at exclusive venues.
                Enjoy personalized menus crafted to your preferences and dietary requirements.
              </p>
            </div>
            <div className="feature-card">
              <h3>Culinary Events & Tastings</h3>
              <p>
                Invitations to exclusive wine tastings, chef's table experiences, and private culinary events
                featuring industry icons and rising stars.
              </p>
            </div>
          </div>
          <p className="tribune-exclusive">This premium benefit is exclusively available to Tribune cardholders</p>
        </section>

        <section id="jet-share" className="benefit-section tribune-only">
          <div className="section-icon">🛩️</div>
          <div className="tribune-badge">Tribune Exclusive</div>
          <h2>Tribune Private Jet Share</h2>
          <div className="section-description">
            <p>
              Travel on your terms with access to our exclusive private jet share program.
              Experience the ultimate in luxury, flexibility, and privacy for both business and leisure travel.
            </p>
          </div>
          <div className="benefit-features">
            <div className="feature-card">
              <h3>On-Demand Charter Access</h3>
              <p>
                Book private jet flights with as little as 24 hours notice. Access a fleet of our very own light, 
                midsize, and heavy jets to match your journey requirements.
              </p>
            </div>
            <div className="feature-card">
              <h3>Time is Money. Save Both.</h3>
              <p>
                While commercial travelers waste hours in security lines and layovers, you're already at your destination. 
                Arrive 15 minutes before departure, skip the crowds, and reclaim your time.
              </p>
            </div>
            <div className="feature-card">
              <h3>Fly On Your Terms</h3>
              <p>
                No jet cards or upfront deposits required. Pay only for the flights you take with preferred
                Tribune member pricing up to 25% below standard charter rates.
              </p>
            </div>
          </div>

          <div className="jet-share-details">
            <h3>Fleet & Services</h3>
            <div className="detail-columns">
              <div className="detail-column">
                <h4>Aircraft Categories</h4>
                <ul>
                  <li>Light Jets (6-8 passengers)</li>
                  <li>Midsize Jets (8-10 passengers)</li>
                  <li>Super Midsize Jets (9-12 passengers)</li>
                  <li>Heavy Jets (12-16 passengers)</li>
                </ul>
              </div>
              <div className="detail-column">
                <h4>Premium Services</h4>
                <ul>
                  <li>Custom catering and beverages available</li>
                  <li>Ground transportation coordination</li>
                  <li>Pet-friendly flights available</li>
                  <li>In-flight WiFi and entertainment</li>
                </ul>
              </div>
            </div>
          </div>

          <p className="tribune-exclusive">This exceptional benefit is exclusively available to Tribune cardholders</p>
        </section>
      </div>
    </div>
  );
};
