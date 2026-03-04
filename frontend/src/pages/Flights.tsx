import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getCachedUser, fetchCurrentUser } from '../utils/auth';
import { getFlights, bookFlight } from '../utils/api';
import type { Flight, FlightFilters } from '../types/flights';
import './Flights.css';

const POINTS_TO_DOLLAR_RATE = 100; // 100 points = $1

const DESTINATION_COUNTRIES: { [key: string]: string } = {
  'Argentina': 'ARG',
  'Brazil': 'BRA',
  'Mexico': 'MEX',
  'Japan': 'JPN',
  'Spain': 'SPA',
  'Italy': 'ITA'
};

const FLIGHT_CLASSES = ['economy', 'premium-economy', 'business', 'first'];

const AIRPORT_NAMES: { [key: string]: string } = {
  'EZE': 'Buenos Aires, Argentina',
  'COR': 'Córdoba, Argentina',
  'GRU': 'São Paulo, Brazil',
  'GIG': 'Rio de Janeiro, Brazil',
  'MEX': 'Mexico City, Mexico',
  'CUN': 'Cancún, Mexico',
  'GDL': 'Guadalajara, Mexico',
  'NRT': 'Tokyo (Narita), Japan',
  'HND': 'Tokyo (Haneda), Japan',
  'KIX': 'Osaka, Japan',
  'MAD': 'Madrid, Spain',
  'BCN': 'Barcelona, Spain',
  'FCO': 'Rome, Italy',
  'MXP': 'Milan, Italy',
  'VCE': 'Venice, Italy',
  'JFK': 'New York (JFK)',
  'MIA': 'Miami',
  'LAX': 'Los Angeles',
  'BOS': 'Boston',
  'ATL': 'Atlanta',
  'SEA': 'Seattle',
  'SFO': 'San Francisco'
};

export function Flights() {
  const navigate = useNavigate();
  const [user, setUser] = useState(getCachedUser());
  const [flights, setFlights] = useState<Flight[]>([]);
  const [filteredFlights, setFilteredFlights] = useState<Flight[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedFlight, setSelectedFlight] = useState<Flight | null>(null);
  const [bookingLoading, setBookingLoading] = useState(false);
  const [bookingError, setBookingError] = useState<string | null>(null);
  const [bookingSuccess, setBookingSuccess] = useState(false);
  const [passengers, setPassengers] = useState(1);
  const [paymentMethod, setPaymentMethod] = useState<'card' | 'points'>('card');

  const [filters, setFilters] = useState<FlightFilters>({
    destinationCountry: '',
    flightClass: '',
    minPrice: 0,
    maxPrice: 15000,
  });

  useEffect(() => {
    const loadData = async () => {
      try {
        if (!user) {
          const fetchedUser = await fetchCurrentUser();
          setUser(fetchedUser);
        }
        const flightsData = await getFlights();
        setFlights(flightsData);
        setFilteredFlights(flightsData);
      } catch (error) {
        console.error('Error loading data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [user]);

  useEffect(() => {
    let filtered = [...flights];

    if (filters.destinationCountry) {
      const countryCode = DESTINATION_COUNTRIES[filters.destinationCountry];
      filtered = filtered.filter(flight => flight.id.includes(`-${countryCode.toLowerCase()}-`));
    }

    if (filters.flightClass) {
      filtered = filtered.filter(flight => flight.class === filters.flightClass);
    }

    filtered = filtered.filter(flight =>
      flight.price >= filters.minPrice && flight.price <= filters.maxPrice
    );

    setFilteredFlights(filtered);
  }, [filters, flights]);

  const handleBookFlight = async () => {
    if (!selectedFlight || !user) return;

    setBookingLoading(true);
    setBookingError(null);
    setBookingSuccess(false);

    try {
      const totalCost = selectedFlight.price * passengers;
      const pointsCost = totalCost * POINTS_TO_DOLLAR_RATE;

      if (paymentMethod === 'card') {
        if (!user.availableCredit || user.availableCredit < totalCost) {
          throw new Error(`Insufficient credit. Available: $${user.availableCredit?.toFixed(2) || 0}, Required: $${totalCost.toFixed(2)}`);
        }
      } else {
        if (user.rewardPoints < pointsCost) {
          throw new Error(`Insufficient points. Available: ${user.rewardPoints.toFixed(0)}, Required: ${pointsCost.toFixed(0)}`);
        }
      }

      const response = await bookFlight({
        flightId: selectedFlight.id,
        paymentMethod,
        passengers,
      });

      // Update local user state
      if (paymentMethod === 'card') {
        setUser({
          ...user,
          availableCredit: response.updatedUser.availableCredit || user.availableCredit,
          rewardPoints: response.updatedUser.rewardPoints,
        });
      } else {
        setUser({
          ...user,
          rewardPoints: response.updatedUser.rewardPoints,
        });
      }

      setBookingSuccess(true);
      setTimeout(() => {
        setSelectedFlight(null);
        setBookingSuccess(false);
      }, 3000);
    } catch (error) {
      setBookingError(error instanceof Error ? error.message : 'Booking failed');
    } finally {
      setBookingLoading(false);
    }
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price);
  };

  const formatDateTime = (isoString: string) => {
    const date = new Date(isoString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  };

  const formatClassDisplay = (flightClass: string) => {
    return flightClass.split('-').map(word =>
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  if (!user) {
    return (
      <div className="flights-page">
        <div className="auth-gate">
          <div className="gate-icon">✈️</div>
          <h1 className="gate-title">Flight Bookings</h1>
          <p className="gate-subtitle">
            Sign in to browse and book flights with your Meridian card
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

  if (loading) {
    return (
      <div className="flights-page">
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading flights...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flights-page">
      <div className="flights-header">
        <h1>Book Your Flight</h1>
        <p>Discover flights to exciting destinations around the world</p>
        {user.availableCredit !== null && (
          <div className="user-credits">
            <div className="credit-item">
              <span className="credit-label">Available Credit:</span>
              <span className="credit-value">{formatPrice(user.availableCredit)}</span>
            </div>
            <div className="credit-item">
              <span className="credit-label">Reward Points:</span>
              <span className="credit-value">{user.rewardPoints.toFixed(0)} pts</span>
            </div>
            <div className="credit-item conversion">
              <span className="conversion-note">{POINTS_TO_DOLLAR_RATE} points = $1</span>
            </div>
          </div>
        )}
      </div>

      <div className="flights-filters">
        <div className="filter-group">
          <label>Destination Country</label>
          <select
            value={filters.destinationCountry}
            onChange={(e) => setFilters({ ...filters, destinationCountry: e.target.value })}
          >
            <option value="">All Countries</option>
            {Object.keys(DESTINATION_COUNTRIES).map(country => (
              <option key={country} value={country}>{country}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>Flight Class</label>
          <select
            value={filters.flightClass}
            onChange={(e) => setFilters({ ...filters, flightClass: e.target.value })}
          >
            <option value="">All Classes</option>
            {FLIGHT_CLASSES.map(flightClass => (
              <option key={flightClass} value={flightClass}>
                {formatClassDisplay(flightClass)}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>Price Range: {formatPrice(filters.minPrice)} - {formatPrice(filters.maxPrice)}</label>
          <div className="price-range-inputs">
            <input
              type="number"
              placeholder="Min"
              value={filters.minPrice}
              onChange={(e) => setFilters({ ...filters, minPrice: Number(e.target.value) })}
              min="0"
            />
            <span>to</span>
            <input
              type="number"
              placeholder="Max"
              value={filters.maxPrice}
              onChange={(e) => setFilters({ ...filters, maxPrice: Number(e.target.value) })}
              min="0"
            />
          </div>
        </div>

        <button
          className="reset-filters-button"
          onClick={() => setFilters({
            destinationCountry: '',
            flightClass: '',
            minPrice: 0,
            maxPrice: 15000,
          })}
        >
          Reset Filters
        </button>
      </div>

      <div className="flights-count">
        Showing {filteredFlights.length} flight{filteredFlights.length !== 1 ? 's' : ''}
      </div>

      <div className="flights-grid">
        {filteredFlights.map(flight => (
          <div key={flight.id} className="flight-card" onClick={() => setSelectedFlight(flight)}>
            <div className="flight-card-header">
              <div className="airline-info">
                <div className="airline-logo-placeholder">
                  <span>{flight.airline}</span>
                </div>
                <div className="flight-number">{flight.flightNumber}</div>
              </div>
              <div className={`flight-class-badge ${flight.class}`}>
                {formatClassDisplay(flight.class)}
              </div>
            </div>

            <div className="flight-route">
              <div className="airport">
                <div className="airport-code">{flight.origin}</div>
                <div className="airport-name">{AIRPORT_NAMES[flight.origin] || flight.origin}</div>
                <div className="flight-time">{formatDateTime(flight.departureDate)}</div>
              </div>
              <div className="flight-arrow">
                <div className="flight-duration">{flight.duration}</div>
                <div className="arrow">→</div>
                {flight.stops > 0 && (
                  <div className="stops-indicator">{flight.stops} stop{flight.stops > 1 ? 's' : ''}</div>
                )}
              </div>
              <div className="airport">
                <div className="airport-code">{flight.destination}</div>
                <div className="airport-name">{AIRPORT_NAMES[flight.destination] || flight.destination}</div>
                <div className="flight-time">{formatDateTime(flight.arrivalDate)}</div>
              </div>
            </div>

            <div className="flight-card-footer">
              <div className="flight-price">
                <span className="price-label">From</span>
                <span className="price-value">{formatPrice(flight.price)}</span>
                <span className="price-subtext">per person</span>
              </div>
              <button className="book-flight-button">
                View Details
              </button>
            </div>
          </div>
        ))}
      </div>

      {filteredFlights.length === 0 && (
        <div className="no-results">
          <div className="no-results-icon">✈️</div>
          <h3>No flights found</h3>
          <p>Try adjusting your filters to see more options</p>
        </div>
      )}

      {selectedFlight && (
        <div className="booking-modal-overlay" onClick={() => setSelectedFlight(null)}>
          <div className="booking-modal" onClick={(e) => e.stopPropagation()}>
            <button className="close-modal" onClick={() => setSelectedFlight(null)}>×</button>

            <h2>Book Your Flight</h2>

            <div className="modal-flight-details">
              <div className="modal-airline">
                <div className="airline-logo-placeholder large">
                  <span>{selectedFlight.airline}</span>
                </div>
                <div>
                  <div className="modal-airline-name">{selectedFlight.airline}</div>
                  <div className="modal-flight-number">{selectedFlight.flightNumber}</div>
                  <div className={`modal-class-badge ${selectedFlight.class}`}>
                    {formatClassDisplay(selectedFlight.class)}
                  </div>
                </div>
              </div>

              <div className="modal-route">
                <div className="modal-airport">
                  <div className="modal-airport-code">{selectedFlight.origin}</div>
                  <div className="modal-airport-name">{AIRPORT_NAMES[selectedFlight.origin]}</div>
                  <div className="modal-time">{formatDateTime(selectedFlight.departureDate)}</div>
                </div>
                <div className="modal-flight-info">
                  <div className="modal-duration">{selectedFlight.duration}</div>
                  <div className="modal-arrow">→</div>
                  {selectedFlight.stops > 0 ? (
                    <div className="modal-stops">{selectedFlight.stops} stop{selectedFlight.stops > 1 ? 's' : ''}</div>
                  ) : (
                    <div className="modal-stops direct">Direct</div>
                  )}
                </div>
                <div className="modal-airport">
                  <div className="modal-airport-code">{selectedFlight.destination}</div>
                  <div className="modal-airport-name">{AIRPORT_NAMES[selectedFlight.destination]}</div>
                  <div className="modal-time">{formatDateTime(selectedFlight.arrivalDate)}</div>
                </div>
              </div>
            </div>

            <div className="booking-options">
              <div className="booking-option-group">
                <label>Number of Passengers</label>
                <input
                  type="number"
                  min="1"
                  max="9"
                  value={passengers}
                  onChange={(e) => setPassengers(Number(e.target.value))}
                />
              </div>

              <div className="booking-option-group">
                <label>Payment Method</label>
                <div className="payment-methods">
                  <button
                    className={`payment-method-button ${paymentMethod === 'card' ? 'active' : ''}`}
                    onClick={() => setPaymentMethod('card')}
                  >
                    <div className="payment-method-icon">💳</div>
                    <div className="payment-method-label">Card Credit</div>
                    <div className="payment-method-note">
                      {user.availableCredit !== null
                        ? `Available: ${formatPrice(user.availableCredit)}`
                        : 'N/A'}
                    </div>
                  </button>
                  <button
                    className={`payment-method-button ${paymentMethod === 'points' ? 'active' : ''}`}
                    onClick={() => setPaymentMethod('points')}
                  >
                    <div className="payment-method-icon">⭐</div>
                    <div className="payment-method-label">Reward Points</div>
                    <div className="payment-method-note">
                      Available: {user.rewardPoints.toFixed(0)} pts
                    </div>
                  </button>
                </div>
              </div>
            </div>

            <div className="booking-summary">
              <div className="summary-row">
                <span>Price per person:</span>
                <span>{formatPrice(selectedFlight.price)}</span>
              </div>
              <div className="summary-row">
                <span>Passengers:</span>
                <span>×{passengers}</span>
              </div>
              <div className="summary-row total">
                <span>Total Cost:</span>
                <span>
                  {paymentMethod === 'card'
                    ? formatPrice(selectedFlight.price * passengers)
                    : `${(selectedFlight.price * passengers * POINTS_TO_DOLLAR_RATE).toFixed(0)} points`
                  }
                </span>
              </div>
              {paymentMethod === 'card' && user.rewardPointsMultiplier && (
                <div className="summary-row points-earned">
                  <span>Points to be earned:</span>
                  <span>+{(selectedFlight.price * passengers * user.rewardPointsMultiplier).toFixed(0)} pts</span>
                </div>
              )}
            </div>

            {bookingError && (
              <div className="booking-error">
                {bookingError}
              </div>
            )}

            {bookingSuccess && (
              <div className="booking-success">
                Flight booked successfully!
              </div>
            )}

            <div className="modal-actions">
              <button
                className="cancel-button"
                onClick={() => setSelectedFlight(null)}
                disabled={bookingLoading}
              >
                Cancel
              </button>
              <button
                className="confirm-booking-button"
                onClick={handleBookFlight}
                disabled={bookingLoading}
              >
                {bookingLoading ? 'Processing...' : 'Confirm Booking'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
