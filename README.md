# Travel Planning Agent

An intelligent multi-agent system built with Google ADK that orchestrates specialized subagents to create comprehensive travel plans tailored to your preferences and budget.

## Overview

This application demonstrates the power of agent orchestration by breaking down the complex task of travel planning into manageable, specialized components. A main coordinator agent delegates tasks to specialized subagents, each focusing on a specific aspect of travel planning.

## Architecture

### Main Agent: Travel Planner Orchestrator
The central coordinator that:
- Processes user travel requests
- Delegates tasks to specialized subagents
- Synthesizes information from all subagents
- Ensures budget constraints are met
- Generates a cohesive, final travel plan

### Subagents

#### 1. Flight Search Subagent
**Responsibilities:**
- Search for flights across multiple carriers
- Compare prices, routes, and travel times
- Filter by user preferences (direct flights, specific airlines, departure times)
- Consider layover durations and airport connections
- Return ranked flight options with pros/cons

**Inputs:** Origin, destination, dates, budget, preferences  
**Outputs:** Top 3-5 flight options with pricing and details

#### 2. Accommodation Subagent
**Responsibilities:**
- Search hotels, Airbnbs, vacation rentals, hostels
- Filter by location, price range, and amenities
- Analyze reviews and ratings
- Check proximity to attractions and transportation
- Consider safety and neighborhood quality

**Inputs:** Destination, dates, budget, accommodation type, amenities  
**Outputs:** Ranked accommodation options with details

#### 3. Itinerary Builder Subagent
**Responsibilities:**
- Research local attractions, restaurants, activities
- Create day-by-day schedules
- Optimize routes to minimize travel time
- Check opening hours and seasonal availability
- Balance activities based on user interests (culture, food, adventure, relaxation)
- Suggest backup options for weather-dependent activities

**Inputs:** Destination, trip duration, interests, pace preference  
**Outputs:** Detailed daily itineraries with alternatives

#### 4. Budget Manager Subagent
**Responsibilities:**
- Track costs across all travel components
- Monitor spending against total budget
- Suggest cost-saving alternatives when over budget
- Allocate budget across categories (flights, hotels, food, activities)
- Calculate daily spending limits
- Provide financial summaries and warnings

**Inputs:** Total budget, cost data from other subagents  
**Outputs:** Budget breakdown, recommendations, alerts

## Key Features

- **Intelligent Orchestration**: The main agent coordinates subagents to work together seamlessly
- **Parallel Processing**: Multiple subagents can search simultaneously for faster results
- **Iterative Refinement**: Subagents can be called multiple times to adjust based on constraints
- **Contextual Awareness**: Subagents share relevant context (e.g., hotel location influences itinerary)
- **Budget Optimization**: Automatic rebalancing when initial searches exceed budget
- **Personalization**: Adapts to user preferences, travel style, and priorities

## User Flow

1. **Input Phase**: User provides travel requirements
   - Destination(s)
   - Travel dates
   - Budget
   - Preferences (accommodation type, interests, pace)
   - Special requirements (dietary, accessibility, family-friendly)

2. **Planning Phase**: Orchestrator coordinates subagents
   - Parallel searches for flights and accommodations
   - Budget manager monitors total costs
   - Itinerary builder creates daily plans
   - Iterative refinement if constraints aren't met

3. **Output Phase**: Comprehensive travel plan delivered
   - Complete itinerary with day-by-day breakdown
   - Flight and accommodation bookings ready
   - Budget breakdown showing all costs
   - Maps and directions
   - Booking links and confirmation numbers
   - Downloadable PDF/mobile app export

## Technical Implementation

### Technology Stack
- **Framework**: Google Agent Development Kit (ADK)
- **Language**: Python
- **APIs**: Flight APIs, Hotel APIs, Maps APIs, Weather APIs
- **Data Storage**: Vector database for preferences and past trips
- **Frontend**: Web interface (React) or CLI

### Agent Communication
Agents communicate through structured messages:
```
{
  "agent": "flight_search",
  "status": "complete",
  "data": {
    "options": [...],
    "total_cost": 450.00
  },
  "recommendations": [...]
}
```

### Workflow Example
```
User Request → Orchestrator
                ↓
    ┌───────────┼───────────┐
    ↓           ↓           ↓
Flight     Accommodation  Budget
Search        Search      Manager
    ↓           ↓           ↓
    └───────────┼───────────┘
                ↓
         Budget Check
                ↓
    (Over budget? Refine searches)
                ↓
         Itinerary Builder
                ↓
         Final Plan
```

## Use Cases

- **Solo Travel**: Optimize for personal interests and flexible schedules
- **Family Vacations**: Kid-friendly activities, family accommodations, safety priorities
- **Business Trips**: Efficient schedules, proximity to venues, expense tracking
- **Budget Travel**: Maximize experiences while minimizing costs
- **Group Travel**: Coordinate multiple preferences and split costs
- **Multi-city Tours**: Complex routing and time optimization

## Future Enhancements

- **Real-time Monitoring**: Track flight prices and notify of deals
- **Collaborative Planning**: Multiple users can contribute preferences
- **Past Trip Learning**: Improve recommendations based on feedback
- **Travel Insurance**: Integrate insurance recommendations and quotes
- **Visa & Documentation**: Check requirements and assist with applications
- **Language Support**: Translation and local phrase guides
- **Emergency Assistance**: 24/7 support during trips
- **Social Integration**: Connect with other travelers, share itineraries

## Why Subagents?

This application showcases why subagents are ideal for complex tasks:

1. **Expertise**: Each subagent specializes in one domain
2. **Maintainability**: Update or replace individual agents without affecting others
3. **Scalability**: Add new agents (transportation, visa assistance) easily
4. **Testing**: Test each agent independently
5. **Reusability**: Agents can be used in other travel-related applications
6. **Parallel Execution**: Faster results through concurrent searches
7. **Failure Isolation**: One agent's failure doesn't crash the entire system

## Getting Started

```bash
# Clone the repository
git clone https://github.com/yourusername/travel-planning-agent.git

# Install dependencies
pip install -r requirements.txt

# Set up API keys
cp .env.example .env
# Edit .env with your API keys

# Run the application
python main.py
```

## Contributing

Contributions are welcome! Areas for contribution:
- Additional subagents (car rentals, travel insurance)
- API integrations
- UI improvements
- Documentation
- Test coverage

## License

MIT License - See LICENSE file for details

---

**Built with Google Agent Development Kit**  
Demonstrating practical multi-agent orchestration for real-world applications.