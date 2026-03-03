import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getAccommodations, bookAccommodation } from '../utils/api';
import { getCachedUser, fetchCurrentUser } from '../utils/auth';
import type { Accommodation, AccommodationFilters, AccommodationType, BookingRequest } from '../types/accommodation';
import './Accommodations.css';

export const Accommodations = () => {
  const navigate = useNavigate();
  const [accommodations, setAccommodations] = useState<Accommodation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedAccommodation, setSelectedAccommodation] = useState<Accommodation | null>(null);
  const [isBookingModalOpen, setIsBookingModalOpen] = useState(false);

  // Filters
  const [selectedCountry, setSelectedCountry] = useState<string>('');
  const [selectedType, setSelectedType] = useState<AccommodationType | ''>('');
  const [minPrice, setMinPrice] = useState<number>(0);
  const [maxPrice, setMaxPrice] = useState<number>(10000);
  const [minRating, setMinRating] = useState<number>(0);

  // Booking form
  const [checkInDate, setCheckInDate] = useState('');
  const [checkOutDate, setCheckOutDate] = useState('');
  const [guests, setGuests] = useState(1);
  const [bookingLoading, setBookingLoading] = useState(false);
  const [bookingSuccess, setBookingSuccess] = useState<string | null>(null);
  const [bookingError, setBookingError] = useState<string | null>(null);

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
    loadAccommodations();
  }, [selectedCountry, selectedType, minPrice, maxPrice, minRating]);

  const loadAccommodations = async () => {
    try {
      setLoading(true);
      setError(null);

      const filters: AccommodationFilters = {};
      if (selectedCountry) filters.country = selectedCountry;
      if (selectedType) filters.type = selectedType as AccommodationType;
      if (minPrice > 0) filters.minPrice = minPrice;
      if (maxPrice < 10000) filters.maxPrice = maxPrice;
      if (minRating > 0) filters.minRating = minRating;

      const data = await getAccommodations(filters);
      setAccommodations(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load accommodations');
    } finally {
      setLoading(false);
    }
  };

  const handleCardClick = (accommodation: Accommodation) => {
    setSelectedAccommodation(accommodation);
    setIsBookingModalOpen(true);
    setBookingSuccess(null);
    setBookingError(null);
    // Set default check-in to tomorrow
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    setCheckInDate(tomorrow.toISOString().split('T')[0]);
    // Set default check-out to 3 days from tomorrow
    const checkOut = new Date(tomorrow);
    checkOut.setDate(checkOut.getDate() + 2);
    setCheckOutDate(checkOut.toISOString().split('T')[0]);
    setGuests(1);
  };

  const handleCloseModal = () => {
    setIsBookingModalOpen(false);
    setSelectedAccommodation(null);
    setBookingSuccess(null);
    setBookingError(null);
  };

  const calculateNights = () => {
    if (!checkInDate || !checkOutDate) return 0;
    const checkIn = new Date(checkInDate);
    const checkOut = new Date(checkOutDate);
    const diffTime = checkOut.getTime() - checkIn.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return Math.max(0, diffDays);
  };

  const calculateTotal = () => {
    if (!selectedAccommodation) return 0;
    return selectedAccommodation.pricePerNight * calculateNights();
  };

  const handleBooking = async () => {
    if (!user) {
      navigate('/login');
      return;
    }

    if (!selectedAccommodation) return;

    if (!checkInDate || !checkOutDate) {
      setBookingError('Please select check-in and check-out dates');
      return;
    }

    const nights = calculateNights();
    if (nights <= 0) {
      setBookingError('Check-out date must be after check-in date');
      return;
    }

    if (guests < 1 || guests > (selectedAccommodation.maxGuests || 10)) {
      setBookingError(`Number of guests must be between 1 and ${selectedAccommodation.maxGuests || 10}`);
      return;
    }

    const total = calculateTotal();
    if (user.availableCredit !== null && user.availableCredit < total) {
      setBookingError(`Insufficient credit. Available: $${user.availableCredit.toFixed(2)}, Required: $${total.toFixed(2)}`);
      return;
    }

    try {
      setBookingLoading(true);
      setBookingError(null);

      const request: BookingRequest = {
        accommodationId: selectedAccommodation.id,
        checkInDate,
        checkOutDate,
        guests,
      };

      const response = await bookAccommodation(request);

      // Refresh user data to update available credit and reservations
      await fetchCurrentUser();

      setBookingSuccess(
        `Booking confirmed! Total: $${response.reservation.totalAmount.toFixed(2)} for ${response.reservation.nights} night(s). You earned ${response.reservation.rewardPointsEarned.toFixed(0)} reward points!`
      );

      // Close modal after 3 seconds
      setTimeout(() => {
        handleCloseModal();
        // Optionally navigate to account page to see reservation
      }, 3000);
    } catch (err) {
      setBookingError(err instanceof Error ? err.message : 'Booking failed');
    } finally {
      setBookingLoading(false);
    }
  };

  const countries = ['Argentina', 'Brazil', 'Mexico', 'Japan', 'Spain', 'Italy'];
  const types: AccommodationType[] = ['hotel', 'airbnb', 'hostel', 'villa'];

  const renderStars = (rating: number) => {
    return (
      <div className="stars">
        {[1, 2, 3, 4, 5].map((star) => (
          <span key={star} className={star <= rating ? 'star filled' : 'star'}>
            ★
          </span>
        ))}
      </div>
    );
  };

  if (!user) {
    return (
      <div className="accommodations-page">
        <div className="auth-gate">
          <div className="gate-icon">🏨</div>
          <h1 className="gate-title">Accommodations</h1>
          <p className="gate-subtitle">
            Sign in to browse and book accommodations with your Meridian card
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
    );
  }

  return (
    <div className="accommodations-page">
      <div className="accommodations-header">
        <h1>Accommodations</h1>
        <p>Find your perfect stay across the world</p>
      </div>

      <div className="filters-section">
        <div className="filter-group">
          <label>Country</label>
          <select value={selectedCountry} onChange={(e) => setSelectedCountry(e.target.value)}>
            <option value="">All Countries</option>
            {countries.map((country) => (
              <option key={country} value={country}>
                {country}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>Type</label>
          <select value={selectedType} onChange={(e) => setSelectedType(e.target.value as AccommodationType | '')}>
            <option value="">All Types</option>
            {types.map((type) => (
              <option key={type} value={type}>
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>Min Rating</label>
          <select value={minRating} onChange={(e) => setMinRating(Number(e.target.value))}>
            <option value="0">Any</option>
            <option value="3">3+ Stars</option>
            <option value="4">4+ Stars</option>
            <option value="5">5 Stars</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Price Range (per night)</label>
          <div className="price-range">
            <input
              type="number"
              placeholder="Min"
              value={minPrice || ''}
              onChange={(e) => setMinPrice(Number(e.target.value) || 0)}
              min="0"
            />
            <span>-</span>
            <input
              type="number"
              placeholder="Max"
              value={maxPrice === 10000 ? '' : maxPrice}
              onChange={(e) => setMaxPrice(Number(e.target.value) || 10000)}
              min="0"
            />
          </div>
        </div>
      </div>

      {loading && <div className="loading">Loading accommodations...</div>}
      {error && <div className="error-message">{error}</div>}

      <div className="accommodations-grid">
        {accommodations.map((accommodation) => (
          <div
            key={accommodation.id}
            className="accommodation-card"
            onClick={() => handleCardClick(accommodation)}
          >
            <div className="accommodation-image" style={{ backgroundImage: `url(${accommodation.imageUrl})` }}>
              <div className="accommodation-type-badge">
                {accommodation.type.charAt(0).toUpperCase() + accommodation.type.slice(1)}
              </div>
            </div>
            <div className="accommodation-info">
              <h3>{accommodation.name}</h3>
              <p className="location">
                {accommodation.city}, {accommodation.country}
              </p>
              {renderStars(accommodation.rating)}
              <div className="amenities">
                {accommodation.amenities.slice(0, 3).map((amenity, index) => (
                  <span key={index} className="amenity-tag">
                    {amenity}
                  </span>
                ))}
                {accommodation.amenities.length > 3 && (
                  <span className="amenity-tag">+{accommodation.amenities.length - 3} more</span>
                )}
              </div>
              <div className="price">
                <span className="price-amount">${accommodation.pricePerNight}</span>
                <span className="price-unit">/ night</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {accommodations.length === 0 && !loading && !error && (
        <div className="no-results">No accommodations found. Try adjusting your filters.</div>
      )}

      {/* Booking Modal */}
      {isBookingModalOpen && selectedAccommodation && (
        <div className="modal-overlay" onClick={handleCloseModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={handleCloseModal}>
              ×
            </button>

            <div className="modal-header">
              <h2>{selectedAccommodation.name}</h2>
              <p className="modal-location">
                {selectedAccommodation.city}, {selectedAccommodation.country}
              </p>
            </div>

            <div className="modal-body">
              <div className="modal-image" style={{ backgroundImage: `url(${selectedAccommodation.imageUrl})` }} />

              <div className="modal-details">
                <div className="detail-row">
                  {renderStars(selectedAccommodation.rating)}
                </div>
                <div className="detail-row">
                  <span className="detail-label">Type:</span>
                  <span className="detail-value">
                    {selectedAccommodation.type.charAt(0).toUpperCase() + selectedAccommodation.type.slice(1)}
                  </span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Max Guests:</span>
                  <span className="detail-value">{selectedAccommodation.maxGuests}</span>
                </div>
                {selectedAccommodation.bedrooms && (
                  <div className="detail-row">
                    <span className="detail-label">Bedrooms:</span>
                    <span className="detail-value">{selectedAccommodation.bedrooms}</span>
                  </div>
                )}
                {selectedAccommodation.bathrooms && (
                  <div className="detail-row">
                    <span className="detail-label">Bathrooms:</span>
                    <span className="detail-value">{selectedAccommodation.bathrooms}</span>
                  </div>
                )}
                <div className="detail-row">
                  <span className="detail-label">Price per night:</span>
                  <span className="detail-value price-highlight">${selectedAccommodation.pricePerNight}</span>
                </div>
              </div>

              <div className="description">
                <h3>Description</h3>
                <p>{selectedAccommodation.description}</p>
              </div>

              <div className="amenities-full">
                <h3>Amenities</h3>
                <div className="amenities-grid">
                  {selectedAccommodation.amenities.map((amenity, index) => (
                    <span key={index} className="amenity-tag">
                      {amenity}
                    </span>
                  ))}
                </div>
              </div>

              {!bookingSuccess && (
                <div className="booking-form">
                  <h3>Book Your Stay</h3>

                  {!user && (
                    <div className="login-prompt">
                      <p>Please log in to book this accommodation</p>
                      <button className="login-button" onClick={() => navigate('/login')}>
                        Login
                      </button>
                    </div>
                  )}

                  {user && (
                    <>
                      <div className="form-row">
                        <div className="form-group">
                          <label>Check-in Date</label>
                          <input
                            type="date"
                            value={checkInDate}
                            onChange={(e) => setCheckInDate(e.target.value)}
                            min={new Date().toISOString().split('T')[0]}
                          />
                        </div>
                        <div className="form-group">
                          <label>Check-out Date</label>
                          <input
                            type="date"
                            value={checkOutDate}
                            onChange={(e) => setCheckOutDate(e.target.value)}
                            min={checkInDate || new Date().toISOString().split('T')[0]}
                          />
                        </div>
                      </div>

                      <div className="form-group">
                        <label>Number of Guests</label>
                        <input
                          type="number"
                          value={guests}
                          onChange={(e) => setGuests(Number(e.target.value))}
                          min="1"
                          max={selectedAccommodation.maxGuests}
                        />
                      </div>

                      <div className="booking-summary">
                        <div className="summary-row">
                          <span>Nights:</span>
                          <span>{calculateNights()}</span>
                        </div>
                        <div className="summary-row">
                          <span>Price per night:</span>
                          <span>${selectedAccommodation.pricePerNight}</span>
                        </div>
                        <div className="summary-row total">
                          <span>Total:</span>
                          <span>${calculateTotal().toFixed(2)}</span>
                        </div>
                        {user.availableCredit !== null && (
                          <div className="summary-row">
                            <span>Available Credit:</span>
                            <span>${user.availableCredit.toFixed(2)}</span>
                          </div>
                        )}
                      </div>

                      {bookingError && <div className="error-message">{bookingError}</div>}

                      <button
                        className="book-button"
                        onClick={handleBooking}
                        disabled={bookingLoading || calculateNights() <= 0}
                      >
                        {bookingLoading ? 'Processing...' : 'Confirm Booking'}
                      </button>
                    </>
                  )}
                </div>
              )}

              {bookingSuccess && (
                <div className="success-message">
                  <div className="success-icon">✓</div>
                  <p>{bookingSuccess}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
