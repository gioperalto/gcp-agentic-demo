# Travel Data Schema

## Countries
- Argentina
- Brazil
- Mexico
- Japan
- Spain
- Italy

## Data Structure

### Accommodations
```json
{
  "id": "string (unique)",
  "name": "string",
  "type": "hotel | airbnb | hostel | villa",
  "country": "string",
  "city": "string",
  "address": "string",
  "rating": "number (1-5)",
  "pricePerNight": "number (USD)",
  "imageUrl": "string (placeholder)",
  "description": "string",
  "amenities": ["string"],
  "capacity": "number (guests)",
  "affordabilityTier": "budget | mid-range | luxury"
}
```

**Pricing Guidelines:**
- Hostels: $20-80/night
- Airbnb: $60-250/night
- Hotels (3-star): $100-200/night
- Hotels (4-star): $200-400/night
- Hotels (5-star): $400-1000/night
- Villas: $300-1500/night

### Restaurants
```json
{
  "id": "string (unique)",
  "name": "string",
  "country": "string",
  "city": "string",
  "address": "string",
  "cuisine": "string",
  "priceRange": "$ | $$ | $$$ | $$$$",
  "avgPricePerPerson": "number (USD)",
  "rating": "number (1-5)",
  "imageUrl": "string (placeholder)",
  "description": "string",
  "specialties": ["string"],
  "reservationAvailable": "boolean",
  "affordabilityTier": "budget | mid-range | luxury"
}
```

**Pricing Guidelines:**
- $: $10-25 per person
- $$: $25-50 per person
- $$$: $50-100 per person
- $$$$: $100-300 per person

### Flights
```json
{
  "id": "string (unique)",
  "airline": "Delta | JetBlue | Southwest | Iberia | LATAM | ANA | JAL",
  "origin": "string (airport code)",
  "destination": "string (airport code)",
  "departureDate": "string (ISO date)",
  "arrivalDate": "string (ISO date)",
  "flightNumber": "string",
  "class": "economy | premium-economy | business | first",
  "price": "number (USD)",
  "duration": "string (e.g., '12h 30m')",
  "stops": "number",
  "imageUrl": "string (placeholder - airline logo)"
}
```

**Pricing Guidelines (International flights from US):**
- Economy: $500-1200
- Premium Economy: $1200-2000
- Business: $2500-6000
- First Class: $5000-15000

### Experiences/Attractions
```json
{
  "id": "string (unique)",
  "name": "string",
  "country": "string",
  "city": "string",
  "type": "hiking | atv | boat-tour | yacht | winery-tour | farm-to-table | cultural | adventure",
  "price": "number (USD per person)",
  "duration": "string (e.g., '4 hours', 'Full day')",
  "rating": "number (1-5)",
  "imageUrl": "string (placeholder)",
  "description": "string",
  "minParticipants": "number",
  "maxParticipants": "number",
  "includedItems": ["string"],
  "affordabilityTier": "budget | mid-range | luxury"
}
```

**Pricing Guidelines:**
- Budget experiences: $30-100 per person
- Mid-range experiences: $100-300 per person
- Luxury experiences: $300-1500 per person

## Affordability Tiers

### Budget (Legionnaire)
- Focus on hostels, budget hotels, Airbnbs
- $ to $$ restaurants
- Economy flights
- Budget to mid-range experiences

### Luxury (Tribune)
- Focus on 5-star hotels, luxury villas
- $$$ to $$$$ restaurants
- Business/First class flights
- Mid-range to luxury experiences
