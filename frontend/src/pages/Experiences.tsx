import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getCachedUser, fetchCurrentUser } from '../utils/auth';
import { getExperiences, bookExperience } from '../utils/api';
import type { Experience, ExperienceType } from '../types/experience';
import './Experiences.css';

export const Experiences = () => {
  const navigate = useNavigate();
  const [experiences, setExperiences] = useState<Experience[]>([]);
  const [filteredExperiences, setFilteredExperiences] = useState<Experience[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filter states
  const [selectedCountry, setSelectedCountry] = useState<string>('');
  const [selectedType, setSelectedType] = useState<string>('');
  const [priceRange, setPriceRange] = useState<[number, number]>([0, 10000]);

  // Booking modal states
  const [selectedExperience, setSelectedExperience] = useState<Experience | null>(null);
  const [bookingDate, setBookingDate] = useState('');
  const [participants, setParticipants] = useState(1);
  const [bookingLoading, setBookingLoading] = useState(false);
  const [bookingError, setBookingError] = useState<string | null>(null);
  const [bookingSuccess, setBookingSuccess] = useState(false);

  const [user, setUser] = useState(getCachedUser());

  useEffect(() => {
    const loadUser = async () => {
      if (!user) {
        const fetchedUser = await fetchCurrentUser();
        setUser(fetchedUser);
      }
    };
    loadUser();
  }, []);

  useEffect(() => {
    loadExperiences();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [experiences, selectedCountry, selectedType, priceRange]);

  const loadExperiences = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getExperiences();
      setExperiences(data);
      setFilteredExperiences(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load experiences');
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...experiences];

    if (selectedCountry) {
      filtered = filtered.filter(exp => exp.country === selectedCountry);
    }

    if (selectedType) {
      filtered = filtered.filter(exp => exp.type === selectedType);
    }

    filtered = filtered.filter(
      exp => exp.price >= priceRange[0] && exp.price <= priceRange[1]
    );

    setFilteredExperiences(filtered);
  };

  const getUniqueCountries = (): string[] => {
    return Array.from(new Set(experiences.map(exp => exp.country))).sort();
  };

  const experienceTypes: ExperienceType[] = [
    'hiking',
    'atv',
    'boat-ride',
    'yacht-ride',
    'winery-tour',
    'farm-to-table',
    'cultural',
    'adventure',
    'other'
  ];

  const formatType = (type: string): string => {
    return type
      .split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const openBookingModal = (experience: Experience) => {
    if (!user) {
      navigate('/login');
      return;
    }

    if (!user.currentCard) {
      alert('You need a Meridian card to book experiences. Please apply for a card first.');
      navigate('/apply');
      return;
    }

    setSelectedExperience(experience);
    setParticipants(experience.minParticipants);
    setBookingDate('');
    setBookingError(null);
    setBookingSuccess(false);
  };

  const closeBookingModal = () => {
    setSelectedExperience(null);
    setBookingDate('');
    setParticipants(1);
    setBookingError(null);
    setBookingSuccess(false);
  };

  const handleBooking = async () => {
    if (!user || !selectedExperience) return;

    if (!bookingDate) {
      setBookingError('Please select a date');
      return;
    }

    if (participants < selectedExperience.minParticipants || participants > selectedExperience.maxParticipants) {
      setBookingError(`Participants must be between ${selectedExperience.minParticipants} and ${selectedExperience.maxParticipants}`);
      return;
    }

    const totalCost = selectedExperience.price * participants;

    if (!user.availableCredit || user.availableCredit < totalCost) {
      setBookingError(`Insufficient credit. You need $${totalCost.toFixed(2)} but only have $${(user.availableCredit || 0).toFixed(2)} available.`);
      return;
    }

    try {
      setBookingLoading(true);
      setBookingError(null);

      const response = await bookExperience({
        userId: user.id,
        itemId: selectedExperience.id,
        participants,
        date: bookingDate,
      });

      if (response.success) {
        setBookingSuccess(true);
        // Refresh user data to update available credit and reservations
        await fetchCurrentUser();

        setTimeout(() => {
          closeBookingModal();
          // Optionally navigate to account page to see booking
        }, 2000);
      } else {
        setBookingError(response.message || 'Booking failed');
      }
    } catch (err) {
      setBookingError(err instanceof Error ? err.message : 'Failed to book experience');
    } finally {
      setBookingLoading(false);
    }
  };

  const getTotalCost = (): number => {
    return selectedExperience ? selectedExperience.price * participants : 0;
  };

  const getRewardPoints = (): number => {
    if (!user || !user.rewardPointsMultiplier) return 0;
    return getTotalCost() * user.rewardPointsMultiplier;
  };

  if (!user) {
    return (
      <div className="experiences-page experiences-hero-bg">
        <div className="experiences-hero-overlay">
          <div className="auth-gate">
            <h1 className="gate-title">Experiences & Adventures</h1>
            <p className="gate-subtitle">
              Sign in to book unforgettable experiences with your Meridian card
            </p>
            <div className="gate-actions">
              <button className="gate-button premium" onClick={() => navigate('/login')}>
                Sign In to Continue
              </button>
              <button className="gate-button secondary" onClick={() => navigate('/cards')}>
                Learn About Our Cards
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="experiences-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading experiences...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="experiences-page">
        <div className="error-container">
          <h2>Error Loading Experiences</h2>
          <p>{error}</p>
          <button onClick={loadExperiences} className="retry-button">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="experiences-page">
      <div className="experiences-header">
        <h1>Experiences & Adventures</h1>
        <p>Create unforgettable memories with our curated selection of unique experiences</p>
      </div>

      <div className="experiences-container">
        <aside className="filters-sidebar">
          <h2>Filters</h2>

          <div className="filter-group">
            <label htmlFor="country-filter">Country</label>
            <select
              id="country-filter"
              value={selectedCountry}
              onChange={(e) => setSelectedCountry(e.target.value)}
              className="filter-select"
            >
              <option value="">All Countries</option>
              {getUniqueCountries().map(country => (
                <option key={country} value={country}>{country}</option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label htmlFor="type-filter">Experience Type</label>
            <select
              id="type-filter"
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="filter-select"
            >
              <option value="">All Types</option>
              {experienceTypes.map(type => (
                <option key={type} value={type}>{formatType(type)}</option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label>Price Range</label>
            <div className="price-range-display">
              ${priceRange[0]} - ${priceRange[1]}
            </div>
            <input
              type="range"
              min="0"
              max="10000"
              step="50"
              value={priceRange[1]}
              onChange={(e) => setPriceRange([priceRange[0], parseInt(e.target.value)])}
              className="price-slider"
            />
          </div>

          <button
            onClick={() => {
              setSelectedCountry('');
              setSelectedType('');
              setPriceRange([0, 10000]);
            }}
            className="clear-filters-button"
          >
            Clear Filters
          </button>
        </aside>

        <main className="experiences-grid-container">
          {filteredExperiences.length === 0 ? (
            <div className="no-results">
              <h3>No experiences found</h3>
              <p>Try adjusting your filters to see more options</p>
            </div>
          ) : (
            <div className="experiences-grid">
              {filteredExperiences.map(experience => (
                <div key={experience.id} className="experience-card">
                  <div
                    className="experience-image"
                    style={{ backgroundImage: `url(${experience.imageUrl})` }}
                  >
                    <div className="experience-type-badge">
                      {formatType(experience.type)}
                    </div>
                    <div className="experience-tier-badge">
                      {experience.affordabilityTier}
                    </div>
                  </div>

                  <div className="experience-content">
                    <h3 className="experience-name">{experience.name}</h3>

                    <div className="experience-location">
                      <span className="location-icon">📍</span>
                      {experience.city}, {experience.country}
                    </div>

                    <div className="experience-rating">
                      <span className="stars">{'⭐'.repeat(Math.round(experience.rating))}</span>
                      <span className="rating-number">{experience.rating.toFixed(1)}</span>
                    </div>

                    <p className="experience-description">{experience.description}</p>

                    <div className="experience-details">
                      <div className="detail-item">
                        <span className="detail-icon">⏱️</span>
                        <span>{experience.duration}</span>
                      </div>
                      <div className="detail-item">
                        <span className="detail-icon">👥</span>
                        <span>{experience.minParticipants}-{experience.maxParticipants} people</span>
                      </div>
                    </div>

                    <div className="experience-included">
                      <h4>What's Included:</h4>
                      <ul>
                        {experience.includedItems.slice(0, 3).map((item, index) => (
                          <li key={index}>{item}</li>
                        ))}
                      </ul>
                    </div>

                    <div className="experience-footer">
                      <div className="experience-price">
                        <span className="price-label">From</span>
                        <span className="price-amount">${experience.price.toFixed(2)}</span>
                        <span className="price-unit">per person</span>
                      </div>
                      <button
                        onClick={() => openBookingModal(experience)}
                        className="book-button"
                      >
                        Book Now
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </main>
      </div>

      {selectedExperience && (
        <div className="booking-modal-overlay" onClick={closeBookingModal}>
          <div className="booking-modal" onClick={(e) => e.stopPropagation()}>
            <button className="close-modal-button" onClick={closeBookingModal}>
              ×
            </button>

            <h2>Book {selectedExperience.name}</h2>

            {bookingSuccess ? (
              <div className="booking-success">
                <div className="success-icon">✓</div>
                <h3>Booking Confirmed!</h3>
                <p>Your experience has been successfully booked.</p>
                <p className="success-detail">
                  You earned {getRewardPoints().toFixed(0)} reward points!
                </p>
              </div>
            ) : (
              <>
                <div className="booking-details">
                  <div className="booking-info">
                    <p>
                      <strong>Location:</strong> {selectedExperience.city}, {selectedExperience.country}
                    </p>
                    <p>
                      <strong>Duration:</strong> {selectedExperience.duration}
                    </p>
                    <p>
                      <strong>Group Size:</strong> {selectedExperience.minParticipants}-{selectedExperience.maxParticipants} participants
                    </p>
                  </div>

                  <div className="booking-form">
                    <div className="form-group">
                      <label htmlFor="booking-date">Date</label>
                      <input
                        type="date"
                        id="booking-date"
                        value={bookingDate}
                        onChange={(e) => setBookingDate(e.target.value)}
                        min={new Date().toISOString().split('T')[0]}
                        className="form-input"
                        required
                      />
                    </div>

                    <div className="form-group">
                      <label htmlFor="participants">Number of Participants</label>
                      <input
                        type="number"
                        id="participants"
                        value={participants}
                        onChange={(e) => setParticipants(parseInt(e.target.value))}
                        min={selectedExperience.minParticipants}
                        max={selectedExperience.maxParticipants}
                        className="form-input"
                        required
                      />
                      <small className="form-help">
                        Min: {selectedExperience.minParticipants}, Max: {selectedExperience.maxParticipants}
                      </small>
                    </div>
                  </div>

                  <div className="booking-summary">
                    <div className="summary-row">
                      <span>Price per person:</span>
                      <span>${selectedExperience.price.toFixed(2)}</span>
                    </div>
                    <div className="summary-row">
                      <span>Participants:</span>
                      <span>{participants}</span>
                    </div>
                    <div className="summary-row total">
                      <span>Total:</span>
                      <span>${getTotalCost().toFixed(2)}</span>
                    </div>
                    {user?.rewardPointsMultiplier && (
                      <div className="summary-row rewards">
                        <span>Reward Points:</span>
                        <span>+{getRewardPoints().toFixed(0)} points</span>
                      </div>
                    )}
                    {user?.availableCredit && (
                      <div className="summary-row">
                        <span>Available Credit:</span>
                        <span>${user.availableCredit.toFixed(2)}</span>
                      </div>
                    )}
                  </div>

                  {bookingError && (
                    <div className="booking-error">
                      {bookingError}
                    </div>
                  )}

                  <div className="booking-actions">
                    <button
                      onClick={closeBookingModal}
                      className="cancel-button"
                      disabled={bookingLoading}
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleBooking}
                      className="confirm-button"
                      disabled={bookingLoading}
                    >
                      {bookingLoading ? 'Processing...' : 'Confirm Booking'}
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
