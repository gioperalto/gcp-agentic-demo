import { useEffect } from 'react';
import { formatDate, formatValueIfDate } from '../utils/dateFormatter';
import { getImageForType } from '../utils/imageMapper';
import './PreviewModal.css';

interface PreviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  data: any;
  type: string;
}

export function PreviewModal({ isOpen, onClose, data, type }: PreviewModalProps) {
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const renderContent = () => {
    switch (type) {
      case 'flight':
        return (
          <div className="preview-content flight-preview">
            <h2>
              <svg className="preview-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/>
              </svg>
              Flight Details
            </h2>
            <div className="preview-grid">
              <div className="preview-item">
                <span className="preview-label">Flight Number:</span>
                <span className="preview-value">{data.flight_number}</span>
              </div>
              <div className="preview-item">
                <span className="preview-label">Airline:</span>
                <span className="preview-value">{data.airline}</span>
              </div>
              <div className="preview-item">
                <span className="preview-label">Route:</span>
                <span className="preview-value">{data.origin} → {data.destination}</span>
              </div>
              <div className="preview-item">
                <span className="preview-label">Departure:</span>
                <span className="preview-value">{formatDate(data.departure_date)} at {data.departure_time}</span>
              </div>
              <div className="preview-item">
                <span className="preview-label">Arrival:</span>
                <span className="preview-value">{data.arrival_time}</span>
              </div>
              <div className="preview-item">
                <span className="preview-label">Duration:</span>
                <span className="preview-value">{data.duration}</span>
              </div>
              <div className="preview-item">
                <span className="preview-label">Price:</span>
                <span className="preview-value price">${data.price}</span>
              </div>
              <div className="preview-item">
                <span className="preview-label">Type:</span>
                <span className="preview-value">{data.direct ? '✓ Direct' : `${data.stops} stop(s)`}</span>
              </div>
              <div className="preview-item">
                <span className="preview-label">Seats Available:</span>
                <span className="preview-value">{data.seats_available}</span>
              </div>
              {data.return_date && (
                <>
                  <div className="preview-divider">Return Flight</div>
                  <div className="preview-item">
                    <span className="preview-label">Return Date:</span>
                    <span className="preview-value">{formatDate(data.return_date)}</span>
                  </div>
                  <div className="preview-item">
                    <span className="preview-label">Departure:</span>
                    <span className="preview-value">{data.return_departure_time}</span>
                  </div>
                  <div className="preview-item">
                    <span className="preview-label">Arrival:</span>
                    <span className="preview-value">{data.return_arrival_time}</span>
                  </div>
                </>
              )}
            </div>
          </div>
        );

      case 'accommodation':
        const accommodationImage = getImageForType(data, 'accommodation');
        return (
          <div className="preview-content accommodation-preview">
            <h2>
              <svg className="preview-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                <polyline points="9 22 9 12 15 12 15 22"/>
              </svg>
              {data.name || 'Accommodation Details'}
            </h2>
            {accommodationImage && (
              <div className="preview-image-container">
                <img
                  src={accommodationImage}
                  alt={data.type || 'Accommodation'}
                  className="preview-image"
                />
                <div className="image-credit">
                  Generated with Nano Banana
                  <span className="credit-icon">🍌</span>
                </div>
              </div>
            )}
            <div className="preview-grid">
              {data.id && (
                <div className="preview-item">
                  <span className="preview-label">ID:</span>
                  <span className="preview-value">{data.id}</span>
                </div>
              )}
              {data.type && (
                <div className="preview-item">
                  <span className="preview-label">Type:</span>
                  <span className="preview-value">{data.type}</span>
                </div>
              )}
              {data.destination && (
                <div className="preview-item">
                  <span className="preview-label">Location:</span>
                  <span className="preview-value">{data.destination}</span>
                </div>
              )}
              {data.price_per_night && (
                <div className="preview-item">
                  <span className="preview-label">Price per Night:</span>
                  <span className="preview-value price">${data.price_per_night}</span>
                </div>
              )}
              {data.rating && (
                <div className="preview-item">
                  <span className="preview-label">Rating:</span>
                  <span className="preview-value">⭐ {data.rating} {data.reviews_count && `(${data.reviews_count} reviews)`}</span>
                </div>
              )}
              {data.distance_to_center && (
                <div className="preview-item">
                  <span className="preview-label">Distance to Center:</span>
                  <span className="preview-value">{data.distance_to_center}</span>
                </div>
              )}
              {data.check_in && (
                <div className="preview-item">
                  <span className="preview-label">Check-in:</span>
                  <span className="preview-value">{formatDate(data.check_in)}</span>
                </div>
              )}
              {data.check_out && (
                <div className="preview-item">
                  <span className="preview-label">Check-out:</span>
                  <span className="preview-value">{formatDate(data.check_out)}</span>
                </div>
              )}
              {data.available_rooms && (
                <div className="preview-item">
                  <span className="preview-label">Available Rooms:</span>
                  <span className="preview-value">{data.available_rooms}</span>
                </div>
              )}
              {data.amenities && data.amenities.length > 0 && (
                <div className="preview-item full-width">
                  <span className="preview-label">Amenities:</span>
                  <div className="amenities-list">
                    {data.amenities.map((amenity: string, index: number) => (
                      <span key={index} className="amenity-tag">{amenity}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        );

      case 'attraction':
        const attractionImage = getImageForType(data, 'attraction');
        return (
          <div className="preview-content attraction-preview">
            <h2>
              <svg className="preview-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                <circle cx="12" cy="10" r="3"/>
              </svg>
              {data.name || 'Attraction Details'}
            </h2>
            {attractionImage && (
              <div className="preview-image-container">
                <img
                  src={attractionImage}
                  alt={data.type || 'Attraction'}
                  className="preview-image"
                />
                <div className="image-credit">
                  Generated with Nano Banana
                  <span className="credit-icon">🍌</span>
                </div>
              </div>
            )}
            <div className="preview-grid">
              {Object.entries(data).filter(([key]) => key !== 'image_url' && key !== 'name').map(([key, value]) => (
                <div key={key} className="preview-item">
                  <span className="preview-label">{key.replace(/_/g, ' ')}:</span>
                  <span className="preview-value">{formatValueIfDate(key, value)}</span>
                </div>
              ))}
            </div>
          </div>
        );

      case 'restaurant':
        const restaurantImage = getImageForType(data, 'restaurant');
        return (
          <div className="preview-content restaurant-preview">
            <h2>
              <svg className="preview-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M3 2v7c0 1.1.9 2 2 2h4c1.1 0 2-.9 2-2V2M7 2v20M21 15V2M17 2v20M17 8h4"/>
              </svg>
              {data.name || 'Restaurant Details'}
            </h2>
            {restaurantImage && (
              <div className="preview-image-container">
                <img
                  src={restaurantImage}
                  alt={data.cuisine || 'Restaurant'}
                  className="preview-image"
                />
                <div className="image-credit">
                  Generated with Nano Banana
                  <span className="credit-icon">🍌</span>
                </div>
              </div>
            )}
            <div className="preview-grid">
              {Object.entries(data).filter(([key]) => key !== 'image_url' && key !== 'name').map(([key, value]) => (
                <div key={key} className="preview-item">
                  <span className="preview-label">{key.replace(/_/g, ' ')}:</span>
                  <span className="preview-value">{formatValueIfDate(key, value)}</span>
                </div>
              ))}
            </div>
          </div>
        );

      case 'itinerary':
        // Helper function to render schedule items
        const renderSchedule = (schedule: any) => {
          if (Array.isArray(schedule)) {
            return (
              <div className="schedule-list">
                {schedule.map((item: any, index: number) => (
                  <div key={index} className="schedule-item">
                    <div className="schedule-time">{item.time || `Item ${index + 1}`}</div>
                    <div className="schedule-details">
                      {typeof item === 'object' ? (
                        Object.entries(item).map(([k, v]) => (
                          k !== 'time' && (
                            <div key={k} className="schedule-detail-item">
                              <strong>{k.replace(/_/g, ' ')}:</strong> {formatValueIfDate(k, v)}
                            </div>
                          )
                        ))
                      ) : (
                        <div>{String(item)}</div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            );
          } else if (typeof schedule === 'object' && schedule !== null) {
            return (
              <div className="schedule-list">
                {Object.entries(schedule).map(([day, activities]: [string, any]) => (
                  <div key={day} className="schedule-day">
                    <div className="schedule-day-header">{day.replace(/_/g, ' ')}</div>
                    {Array.isArray(activities) ? (
                      <div className="schedule-day-activities">
                        {activities.map((activity: any, idx: number) => (
                          <div key={idx} className="schedule-activity">
                            {typeof activity === 'object' ? (
                              Object.entries(activity).map(([k, v]) => (
                                <div key={k} className="schedule-detail-item">
                                  <strong>{k.replace(/_/g, ' ')}:</strong> {formatValueIfDate(k, v)}
                                </div>
                              ))
                            ) : (
                              <div>{String(activity)}</div>
                            )}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="schedule-day-activities">{String(activities)}</div>
                    )}
                  </div>
                ))}
              </div>
            );
          }
          return <div className="preview-value">{JSON.stringify(schedule, null, 2)}</div>;
        };

        return (
          <div className="preview-content itinerary-preview">
            <h2>
              <svg className="preview-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                <line x1="16" y1="2" x2="16" y2="6"/>
                <line x1="8" y1="2" x2="8" y2="6"/>
                <line x1="3" y1="10" x2="21" y2="10"/>
              </svg>
              Itinerary Details
            </h2>
            <div className="itinerary-container">
              {Object.entries(data).map(([key, value]) => {
                // Check if this is a schedule/itinerary field
                const isScheduleField = key.toLowerCase().includes('schedule') ||
                                       key.toLowerCase().includes('itinerary') ||
                                       key.toLowerCase().includes('activities') ||
                                       key.toLowerCase().includes('days');

                if (isScheduleField && (Array.isArray(value) || typeof value === 'object')) {
                  return (
                    <div key={key} className="itinerary-section">
                      <h3 className="itinerary-section-title">{key.replace(/_/g, ' ')}</h3>
                      {renderSchedule(value)}
                    </div>
                  );
                }

                return (
                  <div key={key} className="preview-item full-width">
                    <span className="preview-label">{key.replace(/_/g, ' ')}:</span>
                    <span className="preview-value">
                      {typeof value === 'object' ? renderSchedule(value) : String(value)}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        );

      case 'budget':
        return (
          <div className="preview-content budget-preview">
            <h2>
              <svg className="preview-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="12" y1="1" x2="12" y2="23"/>
                <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
              </svg>
              Budget Details
            </h2>
            <div className="preview-grid">
              {Object.entries(data).map(([key, value]) => (
                <div key={key} className="preview-item">
                  <span className="preview-label">{key.replace(/_/g, ' ')}:</span>
                  <span className="preview-value price">
                    {typeof value === 'number' && (key.includes('cost') || key.includes('price') || key.includes('budget'))
                      ? `$${value}`
                      : formatValueIfDate(key, value)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        );

      default:
        return (
          <div className="preview-content">
            <h2>Details</h2>
            <pre className="preview-json">{JSON.stringify(data, null, 2)}</pre>
          </div>
        );
    }
  };

  return (
    <div className={`detail-panel ${isOpen ? 'open' : ''}`}>
      <div className="detail-panel-header">
        <h3 className="detail-panel-title">Details</h3>
        <button className="detail-panel-close" onClick={onClose} aria-label="Close">
          ✕
        </button>
      </div>
      <div className="detail-panel-content">
        {renderContent()}
      </div>
    </div>
  );
}
