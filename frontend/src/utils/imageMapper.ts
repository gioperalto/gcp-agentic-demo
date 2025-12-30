/**
 * Image Mapper Utility
 * Maps accommodation types, attraction types, and cuisine types to their corresponding images
 * in the public/img folder structure
 */

/**
 * Get the image path for an accommodation based on its type
 * Types: Hotel, Airbnb, Hostel, Villa
 */
export function getAccommodationImage(type: string): string {
  const typeMap: Record<string, string> = {
    'hotel': '/img/accomodations/hotel.png',
    'airbnb': '/img/accomodations/airbnb.png',
    'hostel': '/img/accomodations/hostel.png',
    'villa': '/img/accomodations/villa.png',
  };

  const normalizedType = type.toLowerCase();
  return typeMap[normalizedType] || '/img/accomodations/hotel.png'; // Default to hotel
}

/**
 * Get the image path for an attraction based on its type
 * Types: Museum, Park, Restaurant, Monument, Beach, Market, Gallery
 */
export function getAttractionImage(type: string): string {
  const typeMap: Record<string, string> = {
    'museum': '/img/attractions/museum.png',
    'park': '/img/attractions/park.png',
    'restaurant': '/img/attractions/restaurant.png',
    'monument': '/img/attractions/monument.png',
    'beach': '/img/attractions/beach.png',
    'market': '/img/attractions/market.png',
    'gallery': '/img/attractions/gallery.png',
  };

  const normalizedType = type.toLowerCase();
  return typeMap[normalizedType] || '/img/attractions/monument.png'; // Default to monument
}

/**
 * Get the image path for a restaurant based on its cuisine type
 * Types: Italian, Japanese, Mexican, French, American, Thai, Fast-Food
 */
export function getRestaurantImage(cuisineType: string): string {
  if (!cuisineType) {
    console.warn('ImageMapper: No cuisine type provided for restaurant');
    return '/img/restaurants/american.png';
  }

  const typeMap: Record<string, string> = {
    'italian': '/img/restaurants/italian.png',
    'japanese': '/img/restaurants/japanese.png',
    'mexican': '/img/restaurants/mexican.png',
    'french': '/img/restaurants/french.png',
    'american': '/img/restaurants/american.png',
    'thai': '/img/restaurants/thai.png',
    'fast-food': '/img/restaurants/fast-food.png',
    'fast food': '/img/restaurants/fast-food.png',
  };

  // Normalize the cuisine type (trim whitespace and convert to lowercase)
  const normalizedType = cuisineType.trim().toLowerCase();

  // Check if we have a mapping for this cuisine type
  const imagePath = typeMap[normalizedType];

  if (!imagePath) {
    console.warn(`ImageMapper: No image found for cuisine type "${cuisineType}" (normalized: "${normalizedType}"). Defaulting to American.`);
    return '/img/restaurants/american.png';
  }

  return imagePath;
}

/**
 * Get image based on data type and category
 * This is a general utility that determines which specific mapper to use
 */
export function getImageForType(data: any, type: string): string | null {
  switch (type) {
    case 'accommodation':
      return data.type ? getAccommodationImage(data.type) : null;

    case 'attraction':
      return data.type ? getAttractionImage(data.type) : null;

    case 'restaurant':
      return data.cuisine ? getRestaurantImage(data.cuisine) : null;

    default:
      return null;
  }
}
