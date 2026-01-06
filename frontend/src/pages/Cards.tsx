import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import type { CreditCard } from '../types/cards';
import { CARDS } from '../data/cardData';
import { CardModal } from '../components/CardModal';
import './Cards.css';

export const Cards = () => {
  const navigate = useNavigate();
  const [selectedCard, setSelectedCard] = useState<CreditCard | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleMoreDetails = (card: CreditCard) => {
    setSelectedCard(card);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedCard(null);
  };

  return (
    <div className="cards-page">
      <div className="cards-header">
        <h1>Our Cards</h1>
        <p>All of our cards are made of metal, reflecting the standard we hold for all of our customers.</p>
        <p>Metal cards are far more durable than those cheap plastic alternatives some of our competitors offer.</p>
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
                  className="details-button"
                  onClick={() => handleMoreDetails(card)}
                >
                  More Details
                </button>
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

      <CardModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        card={selectedCard}
      />
    </div>
  );
};
