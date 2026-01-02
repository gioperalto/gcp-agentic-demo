import './Cards.css';

export const Cards = () => {
  return (
    <div className="cards-page">
      <div className="cards-header">
        <h1>Our Cards</h1>
        <p>All of our cards are made of metal, reflecting the standard we hold for all of our customers.</p>
        <p>Metal cards are far more durable than those cheap plastic alternatives some of our competitors offer.</p>
      </div>

      <div className="cards-container">
        <div className="credit-card legionnaire">
          <div className="card-image-placeholder">
            <div className="image-credit">
              Generated with Nano Banana
              <span className="credit-icon">🍌</span>
            </div>
          </div>
          <div className="card-info">
            <h2 className="card-name">Legionnaire</h2>
            <div className="card-details">
              <div className="card-detail-item">
                <span className="detail-label">Annual Fee:</span>
                <span className="detail-value">$120</span>
              </div>
              <div className="card-detail-item">
                <span className="detail-label">APR range:</span>
                <span className="detail-value">12.99% - 24.99%</span>
              </div>
              <div className="card-detail-item">
                <span className="detail-label">Average credit score:</span>
                <span className="detail-value">720</span>
              </div>
              <div className="card-detail-item">
                <span className="detail-label">Rewards Rate:</span>
                <span className="detail-value">2% on all purchases</span>
              </div>
            </div>
            <div className="card-benefits">
              <h3>Benefits:</h3>
              <ul>
                <li>Travel insurance coverage</li>
                <li>24/7 concierge chat</li>
              </ul>
            </div>
            <button className="apply-button">Apply Now</button>
          </div>
        </div>

        <div className="credit-card tribune">
          <div className="card-image-placeholder">
            <div className="image-credit">
              Generated with Nano Banana
              <span className="credit-icon">🍌</span>
            </div>
          </div>
          <div className="card-info">
            <h2 className="card-name">Tribune</h2>
            <div className="card-details">
              <div className="card-detail-item">
                <span className="detail-label">Annual Fee:</span>
                <span className="detail-value">$10,000</span>
              </div>
              <div className="card-detail-item">
                <span className="detail-label">APR range:</span>
                <span className="detail-value">4.99-9.99%</span>
              </div>
              <div className="card-detail-item">
                <span className="detail-label">Average credit score:</span>
                <span className="detail-value">850</span>
              </div>
              <div className="card-detail-item">
                <span className="detail-label">Rewards Rate:</span>
                <span className="detail-value">Up to 5% on select purchases*</span>
              </div>
            </div>
            <div className="card-benefits">
              <h3>Additional Benefits:</h3>
              <ul>
                <li>Complimentary Tribune lounge access worldwide</li>
                <li>Dedicated personal concierge</li>
                <li>Access to Tribune dining experiences</li>
                <li>Access to Tribune private jet share</li>
              </ul>
            </div>
            <button className="apply-button premium">Apply Now</button>
          </div>
        </div>
      </div>
    </div>
  );
};
