import { useState, useEffect } from 'react';
import { getRestaurants, makeRestaurantReservation } from '../utils/api';
import type { Restaurant, RestaurantFilters, RestaurantReservation } from '../types/restaurant';
import './Restaurants.css';

export function Restaurants() {
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [filteredRestaurants, setFilteredRestaurants] = useState<Restaurant[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedRestaurant, setSelectedRestaurant] = useState<Restaurant | null>(null);
  const [showReservationModal, setShowReservationModal] = useState(false);
  const [reservationSuccess, setReservationSuccess] = useState(false);

  // Filter states
  const [filters, setFilters] = useState<RestaurantFilters>({
    country: '',
    priceRange: [],
    cuisine: '',
    affordabilityTier: '',
    searchQuery: ''
  });

  // Reservation form states
  const [numberOfPeople, setNumberOfPeople] = useState(2);
  const [reservationDate, setReservationDate] = useState('');
  const [reservationTime, setReservationTime] = useState('');
  const [specialRequests, setSpecialRequests] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // Load restaurants
  useEffect(() => {
    loadRestaurants();
  }, []);

  // Apply filters
  useEffect(() => {
    applyFilters();
  }, [restaurants, filters]);

  const loadRestaurants = async () => {
    try {
      setLoading(true);
      const data = await getRestaurants();
      setRestaurants(data);
      setFilteredRestaurants(data);
    } catch (err) {
      setError('Failed to load restaurants');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...restaurants];

    if (filters.country) {
      filtered = filtered.filter(r => r.country === filters.country);
    }

    if (filters.priceRange && filters.priceRange.length > 0) {
      filtered = filtered.filter(r => filters.priceRange!.includes(r.priceRange));
    }

    if (filters.cuisine) {
      filtered = filtered.filter(r => r.cuisine.toLowerCase().includes(filters.cuisine!.toLowerCase()));
    }

    if (filters.affordabilityTier) {
      filtered = filtered.filter(r => r.affordabilityTier === filters.affordabilityTier);
    }

    if (filters.searchQuery) {
      const query = filters.searchQuery.toLowerCase();
      filtered = filtered.filter(r =>
        r.name.toLowerCase().includes(query) ||
        r.cuisine.toLowerCase().includes(query) ||
        r.description.toLowerCase().includes(query) ||
        r.city.toLowerCase().includes(query)
      );
    }

    setFilteredRestaurants(filtered);
  };

  const handlePriceRangeToggle = (range: string) => {
    const currentRanges = filters.priceRange || [];
    const newRanges = currentRanges.includes(range)
      ? currentRanges.filter(r => r !== range)
      : [...currentRanges, range];

    setFilters({ ...filters, priceRange: newRanges });
  };

  const clearFilters = () => {
    setFilters({
      country: '',
      priceRange: [],
      cuisine: '',
      affordabilityTier: '',
      searchQuery: ''
    });
  };

  const openReservationModal = (restaurant: Restaurant) => {
    setSelectedRestaurant(restaurant);
    setShowReservationModal(true);
    setReservationSuccess(false);
    // Set default date to tomorrow
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    setReservationDate(tomorrow.toISOString().split('T')[0]);
    setReservationTime('19:00');
    setNumberOfPeople(2);
    setSpecialRequests('');
  };

  const closeReservationModal = () => {
    setShowReservationModal(false);
    setSelectedRestaurant(null);
    setReservationSuccess(false);
  };

  const handleReservation = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedRestaurant) return;

    const reservation: RestaurantReservation = {
      restaurantId: selectedRestaurant.id,
      restaurantName: selectedRestaurant.name,
      numberOfPeople,
      date: reservationDate,
      time: reservationTime,
      specialRequests: specialRequests || undefined
    };

    try {
      setSubmitting(true);
      await makeRestaurantReservation(reservation);
      setReservationSuccess(true);
    } catch (err) {
      console.error('Reservation failed:', err);
      alert('Failed to make reservation. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  // Get unique countries and cuisines for filters
  const countries = Array.from(new Set(restaurants.map(r => r.country))).sort();
  const cuisines = Array.from(new Set(restaurants.map(r => r.cuisine))).sort();

  if (loading) {
    return (
      <div className="restaurants-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading restaurants...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="restaurants-page">
        <div className="error-container">
          <h2>Error</h2>
          <p>{error}</p>
          <button onClick={loadRestaurants} className="retry-button">Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="restaurants-page">
      <div className="restaurants-header">
        <h1>Restaurants</h1>
        <p>Discover and reserve tables at exceptional dining destinations worldwide</p>
      </div>

      <div className="restaurants-content">
        {/* Filters Sidebar */}
        <aside className="filters-sidebar">
          <div className="filters-header">
            <h3>Filters</h3>
            <button onClick={clearFilters} className="clear-filters-btn">Clear All</button>
          </div>

          {/* Search */}
          <div className="filter-section">
            <label>Search</label>
            <input
              type="text"
              placeholder="Search restaurants..."
              value={filters.searchQuery}
              onChange={(e) => setFilters({ ...filters, searchQuery: e.target.value })}
              className="search-input"
            />
          </div>

          {/* Country Filter */}
          <div className="filter-section">
            <label>Country</label>
            <select
              value={filters.country}
              onChange={(e) => setFilters({ ...filters, country: e.target.value })}
              className="filter-select"
            >
              <option value="">All Countries</option>
              {countries.map(country => (
                <option key={country} value={country}>{country}</option>
              ))}
            </select>
          </div>

          {/* Price Range Filter */}
          <div className="filter-section">
            <label>Price Range</label>
            <div className="checkbox-group">
              {['$', '$$', '$$$', '$$$$'].map(range => (
                <label key={range} className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={filters.priceRange?.includes(range) || false}
                    onChange={() => handlePriceRangeToggle(range)}
                  />
                  <span>{range}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Cuisine Filter */}
          <div className="filter-section">
            <label>Cuisine</label>
            <select
              value={filters.cuisine}
              onChange={(e) => setFilters({ ...filters, cuisine: e.target.value })}
              className="filter-select"
            >
              <option value="">All Cuisines</option>
              {cuisines.map(cuisine => (
                <option key={cuisine} value={cuisine}>{cuisine}</option>
              ))}
            </select>
          </div>

          {/* Affordability Tier Filter */}
          <div className="filter-section">
            <label>Tier</label>
            <select
              value={filters.affordabilityTier}
              onChange={(e) => setFilters({ ...filters, affordabilityTier: e.target.value })}
              className="filter-select"
            >
              <option value="">All Tiers</option>
              <option value="budget">Budget</option>
              <option value="mid-range">Mid-Range</option>
              <option value="luxury">Luxury</option>
            </select>
          </div>

          <div className="results-count">
            Showing {filteredRestaurants.length} of {restaurants.length} restaurants
          </div>
        </aside>

        {/* Restaurants Grid */}
        <main className="restaurants-grid-container">
          {filteredRestaurants.length === 0 ? (
            <div className="no-results">
              <p>No restaurants found matching your criteria.</p>
              <button onClick={clearFilters} className="clear-filters-btn">Clear Filters</button>
            </div>
          ) : (
            <div className="restaurants-grid">
              {filteredRestaurants.map(restaurant => (
                <div key={restaurant.id} className="restaurant-card">
                  <div className="restaurant-image">
                    <img src={restaurant.imageUrl} alt={restaurant.name} />
                    <div className="image-credit">
                      Generated with Nano Banana
                      <span className="credit-icon">🍌</span>
                    </div>
                    <div className="restaurant-price-badge">{restaurant.priceRange}</div>
                  </div>

                  <div className="restaurant-info">
                    <div className="restaurant-header-row">
                      <h3 className="restaurant-name">{restaurant.name}</h3>
                      <div className="restaurant-rating">
                        <span className="rating-star">★</span>
                        <span>{restaurant.rating.toFixed(1)}</span>
                      </div>
                    </div>

                    <p className="restaurant-cuisine">{restaurant.cuisine}</p>
                    <p className="restaurant-location">{restaurant.city}, {restaurant.country}</p>
                    <p className="restaurant-description">{restaurant.description}</p>

                    <div className="restaurant-specialties">
                      <strong>Specialties:</strong>
                      <div className="specialties-tags">
                        {restaurant.specialties.slice(0, 3).map((specialty, idx) => (
                          <span key={idx} className="specialty-tag">{specialty}</span>
                        ))}
                      </div>
                    </div>

                    <div className="restaurant-footer">
                      <div className="restaurant-price">
                        ${restaurant.avgPricePerPerson} avg per person
                      </div>
                      {restaurant.reservationAvailable ? (
                        <button
                          onClick={() => openReservationModal(restaurant)}
                          className="reserve-button"
                        >
                          Reserve Table
                        </button>
                      ) : (
                        <button className="reserve-button disabled" disabled>
                          Not Available
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </main>
      </div>

      {/* Reservation Modal */}
      {showReservationModal && selectedRestaurant && (
        <div className="modal-overlay" onClick={closeReservationModal}>
          <div className="reservation-modal" onClick={(e) => e.stopPropagation()}>
            {!reservationSuccess ? (
              <>
                <div className="modal-header">
                  <h2>Reserve at {selectedRestaurant.name}</h2>
                  <button onClick={closeReservationModal} className="close-button">&times;</button>
                </div>

                <div className="modal-body">
                  <div className="restaurant-summary">
                    <p><strong>Location:</strong> {selectedRestaurant.city}, {selectedRestaurant.country}</p>
                    <p><strong>Cuisine:</strong> {selectedRestaurant.cuisine}</p>
                    <p><strong>Price Range:</strong> {selectedRestaurant.priceRange}</p>
                  </div>

                  <form onSubmit={handleReservation} className="reservation-form">
                    <div className="form-group">
                      <label htmlFor="numberOfPeople">Number of People</label>
                      <input
                        type="number"
                        id="numberOfPeople"
                        min="1"
                        max="20"
                        value={numberOfPeople}
                        onChange={(e) => setNumberOfPeople(parseInt(e.target.value))}
                        required
                      />
                    </div>

                    <div className="form-group">
                      <label htmlFor="reservationDate">Date</label>
                      <input
                        type="date"
                        id="reservationDate"
                        value={reservationDate}
                        onChange={(e) => setReservationDate(e.target.value)}
                        min={new Date().toISOString().split('T')[0]}
                        required
                      />
                    </div>

                    <div className="form-group">
                      <label htmlFor="reservationTime">Time</label>
                      <input
                        type="time"
                        id="reservationTime"
                        value={reservationTime}
                        onChange={(e) => setReservationTime(e.target.value)}
                        required
                      />
                    </div>

                    <div className="form-group">
                      <label htmlFor="specialRequests">Special Requests (Optional)</label>
                      <textarea
                        id="specialRequests"
                        value={specialRequests}
                        onChange={(e) => setSpecialRequests(e.target.value)}
                        placeholder="Dietary restrictions, seating preferences, etc."
                        rows={3}
                      />
                    </div>

                    <div className="modal-footer">
                      <button type="button" onClick={closeReservationModal} className="cancel-button">
                        Cancel
                      </button>
                      <button type="submit" className="submit-button" disabled={submitting}>
                        {submitting ? 'Reserving...' : 'Confirm Reservation'}
                      </button>
                    </div>
                  </form>
                </div>
              </>
            ) : (
              <div className="success-message">
                <div className="success-icon">✓</div>
                <h2>Reservation Confirmed!</h2>
                <p>Your table at <strong>{selectedRestaurant.name}</strong> is reserved for:</p>
                <div className="reservation-details">
                  <p><strong>Date:</strong> {new Date(reservationDate).toLocaleDateString()}</p>
                  <p><strong>Time:</strong> {reservationTime}</p>
                  <p><strong>Party Size:</strong> {numberOfPeople} {numberOfPeople === 1 ? 'person' : 'people'}</p>
                </div>
                <p className="confirmation-note">
                  A confirmation has been sent. We look forward to serving you!
                </p>
                <button onClick={closeReservationModal} className="close-success-button">
                  Close
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
