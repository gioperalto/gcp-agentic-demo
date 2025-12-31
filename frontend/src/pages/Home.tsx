import './Home.css';

export const Home = () => {
  return (
    <div className="home">
      <div className="hero-section">
        <div className="hero-overlay">
          <h1 className="hero-title">Spending never felt so good</h1>
        </div>
        <div className="image-credit">
          Generated with Nano Banana
          <span className="credit-icon">🍌</span>
        </div>
      </div>

      <div className="content-section">
        <div className="stats-container">
          <div className="stat-card">
            <div className="stat-number">2.5M+</div>
            <div className="stat-label">Active Cardholders</div>
            <p className="stat-description">
              Join millions of members who experience premium rewards and exclusive benefits every day.
            </p>
          </div>

          <div className="stat-card">
            <div className="stat-number">$12B+</div>
            <div className="stat-label">Annual Spend</div>
            <p className="stat-description">
              Our cardholders invest in experiences that matter, earning unparalleled rewards along the way.
            </p>
          </div>

          <div className="stat-card">
            <div className="stat-number">98%</div>
            <div className="stat-label">Satisfaction Rate</div>
            <p className="stat-description">
              Experience world-class service and benefits that keep our members coming back year after year.
            </p>
          </div>
        </div>

        <div className="cta-section">
          <h2>Experience Luxury Redefined</h2>
          <p>
            Meridian cards offer more than just credit—they're your passport to extraordinary experiences,
            exclusive access, and rewards that match your lifestyle.
          </p>
          <button className="cta-button" onClick={() => window.location.href = '/cards'}>
            Explore Our Cards
          </button>
        </div>
      </div>
    </div>
  );
};
