# Legionnaire Concierge Agent

The Legionnaire Concierge is a budget-focused AI concierge service designed for Legionnaire cardholders. It provides affordable travel recommendations by referencing local data for accommodations, restaurants, flights, and experiences.

## Features

### Data Access
The agent has access to curated travel data for 6 countries:
- **Argentina** (Buenos Aires, Mendoza, Bariloche, Puerto Iguazú)
- **Brazil** (Rio de Janeiro, São Paulo, Salvador, Manaus)
- **Mexico** (Mexico City, Los Cabos, Playa del Carmen, Oaxaca)
- **Japan** (Tokyo, Kyoto, Osaka, Sapporo)
- **Spain** (Barcelona, Madrid, Seville, Valencia)
- **Italy** (Rome, Venice, Florence, Naples)

### Available Tools

The agent uses four specialized tools to query local data:

#### 1. `search_affordable_accommodations`
Searches for budget and mid-range hotels, hostels, and airbnbs.

**Parameters:**
- `country` (optional): Filter by country name
- `city` (optional): Filter by city name
- `max_price` (optional): Maximum price per night

**Returns:** JSON array of accommodations with:
- `id`: Unique identifier (e.g., "acc-arg-003")
- `name`: Accommodation name
- `type`: Type (hotel, hostel, airbnb, villa)
- `pricePerNight`: Price per night in USD
- `rating`: Rating out of 5
- `affordabilityTier`: "budget" or "mid-range"
- `amenities`: List of amenities
- `description`: Detailed description

#### 2. `search_affordable_restaurants`
Searches for budget and mid-range restaurants.

**Parameters:**
- `country` (optional): Filter by country name
- `city` (optional): Filter by city name
- `max_price` (optional): Maximum average price per person
- `cuisine` (optional): Filter by cuisine type

**Returns:** JSON array of restaurants with:
- `id`: Unique identifier (e.g., "rest-arg-003")
- `name`: Restaurant name
- `cuisine`: Cuisine type
- `avgPricePerPerson`: Average price per person in USD
- `rating`: Rating out of 5
- `affordabilityTier`: "budget" or "mid-range"
- `specialties`: List of specialty dishes
- `description`: Detailed description

#### 3. `search_economy_flights`
Searches for economy and premium-economy flights.

**Parameters:**
- `origin` (optional): Origin airport code (e.g., "JFK", "LAX")
- `destination` (optional): Destination airport code (e.g., "EZE", "GRU")
- `max_price` (optional): Maximum flight price

**Returns:** JSON array of flights with:
- `id`: Unique identifier (e.g., "flt-arg-001")
- `airline`: Airline name
- `flightNumber`: Flight number
- `origin`: Origin airport code
- `destination`: Destination airport code
- `class`: "economy" or "premium-economy"
- `price`: Price in USD
- `duration`: Flight duration
- `stops`: Number of stops

#### 4. `search_affordable_experiences`
Searches for budget and mid-range experiences and activities.

**Parameters:**
- `country` (optional): Filter by country name
- `city` (optional): Filter by city name
- `experience_type` (optional): Filter by type (hiking, boat-tour, winery-tour, farm-to-table, cultural, atv)
- `max_price` (optional): Maximum price per person

**Returns:** JSON array of experiences with:
- `id`: Unique identifier (e.g., "exp-arg-001")
- `name`: Experience name
- `type`: Experience type
- `price`: Price per person in USD
- `duration`: Duration
- `rating`: Rating out of 5
- `affordabilityTier`: "budget" or "mid-range"
- `description`: Detailed description
- `includedItems`: What's included

## Link Format

The agent provides clickable links in responses that keep users within the concierge chat interface:

### Link Syntax
- **Accommodations**: `[Name](/accommodations?id=ITEM_ID)`
- **Restaurants**: `[Name](/restaurants?id=ITEM_ID)`
- **Flights**: `[Name](/flights?id=ITEM_ID)`
- **Experiences**: `[Name](/experiences?id=ITEM_ID)`

### Example Usage
```
I recommend staying at [Art Factory Hostel](/accommodations?id=acc-arg-003)
in Buenos Aires. It's a vibrant hostel in the historic San Telmo neighborhood
with colorful murals and regular tango nights, at just $35 per night.

For dining, check out [El Cuartito](/restaurants?id=rest-arg-003), a historic
pizzeria from 1934 serving authentic Buenos Aires-style pizza at around $18 per person.
```

## Agent Behavior

### Focus on Value
- Prioritizes budget and mid-range options (excludes luxury tier)
- Highlights hostels, airbnbs, and 3-star hotels
- Recommends economy and premium-economy flights only
- Suggests affordable local experiences

### Recommendation Style
- Presents 2-4 options at different price points
- Always includes pricing for transparency
- Mentions ratings and key amenities
- Explains value proposition (why it's a good deal)

### Response Format
When recommending options, the agent:
1. Uses its tools to search local data
2. Filters for affordable options
3. Presents recommendations with clickable links
4. Includes relevant details (price, rating, description)
5. Stays within the concierge chat interface

## Example Interactions

### User: "I'm planning a budget trip to Buenos Aires. Where should I stay?"

**Agent Response:**
"I'd be happy to help you find affordable accommodations in Buenos Aires! Let me search our options...

I found some great budget-friendly places:

1. **[Art Factory Hostel](/accommodations?id=acc-arg-003)** - $35/night ⭐4.0
   - Located in historic San Telmo
   - Vibrant atmosphere with colorful murals and tango nights
   - Perfect for backpackers and budget travelers
   - Amenities: Free WiFi, shared kitchen, bar, laundry

2. **[Palermo Soho Loft](/accommodations?id=acc-arg-002)** - $120/night ⭐4.5
   - Modern loft in trendy Palermo Soho
   - Walking distance to boutiques and cafes
   - Sleeps up to 4 people
   - Amenities: WiFi, kitchen, workspace, A/C

3. **[Casa Moderna Belgrano](/accommodations?id=acc-arg-004)** - $145/night ⭐3.0
   - Comfortable 3-star hotel in Belgrano
   - Great value with free breakfast included
   - Easy metro access

Which type of accommodation interests you most?"

### User: "Where can I get cheap but good food in Buenos Aires?"

**Agent Response:**
"Buenos Aires has amazing affordable dining options! Here are my top picks:

1. **[El Cuartito](/restaurants?id=rest-arg-003)** - ~$18/person ⭐4.3
   - Historic pizzeria established in 1934
   - Authentic Buenos Aires-style pizza with thick crusts
   - Try the Fugazzeta or Mozzarella pizza!

2. **[Café Tortoni](/restaurants?id=rest-arg-005)** - ~$22/person ⭐4.4
   - Buenos Aires' oldest café (opened 1858)
   - Cultural landmark with traditional café fare
   - Don't miss the medialunas and hot chocolate

3. **[La Cocina Porteña](/restaurants?id=rest-arg-007)** - ~$35/person ⭐4.5
   - Cozy neighborhood spot with authentic home cooking
   - Fresh empanadas and daily specials
   - Great value for traditional Argentine dishes

All of these offer excellent food at budget-friendly prices!"

## Technical Implementation

### File Structure
```
legionnaire_concierge/
├── __init__.py          # Module exports
├── agent.py             # Agent configuration
├── tools.py             # Search tool implementations
└── README.md            # This file
```

### Data Sources
Tools read from JSON files located in:
```
backend/data/
├── accommodations.json
├── restaurants.json
├── flights.json
└── experiences.json
```

### Integration
The agent is integrated into the backend API at:
- **Endpoint**: `POST /api/chat/legionnaire/stream`
- **Runner**: `InMemoryRunner` with session management
- **Streaming**: Server-Sent Events (SSE)

## Testing

Run the test script to verify tool functionality:
```bash
python3 test_legionnaire_tools.py
```

Expected output shows successful queries for:
- Accommodations in Buenos Aires
- Restaurants in Rio de Janeiro
- Flights to Mexico City
- Hiking experiences in Spain

## Future Enhancements

Potential improvements:
- Add real-time availability checking
- Integrate booking capabilities
- Add user preference learning
- Support more destinations
- Add price comparison features
- Include currency conversion
- Add seasonal pricing insights
