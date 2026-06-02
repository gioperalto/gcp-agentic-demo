# Tribune Concierge — Premium Multi-Agent Travel Team

The Tribune Concierge is a high-end AI travel team for Tribune cardholders. A lead coordinator delegates to specialized sub-agents, each with deep expertise in a travel domain. All recommendations skew toward premium options with no assumed budget constraints.

## Agents

| Agent | Role | Tools file |
|-------|------|-----------|
| **Sam** | Lead coordinator — understands traveler needs and delegates to specialists | `agent.py` |
| **Jenny** | Flight search specialist — first-class and business-class options | `tools/jenny.py` |
| **Marcus** | Accommodation expert — luxury hotels, villas, and 5-star properties | `tools/marcus.py` |
| **Sofia** | Itinerary planner and local attractions specialist | `tools/sofia.py` / `tools/attractions.py` |
| **Luca** | Restaurant and fine-dining recommendations specialist | `tools/luca.py` / `tools/restaurants.py` |
| **Ralph** | Experimental agent (gated by `ralph_agent` feature flag) | `tools/ralph.py` |

## Available Tools

Each specialist agent uses typed tools that query the JSON seed data in `backend/data/`:

- `search_luxury_accommodations` — villas, 5-star hotels, premium airbnbs filtered by country/city/price
- `search_premium_restaurants` — fine-dining and upscale restaurants
- `search_premium_flights` — business/first-class flights from major airlines
- `search_premium_experiences` — yacht rides, winery tours, private ATV excursions, farm-to-table dinners

## Link Format

Agent responses embed clickable links that keep users within the concierge chat (no page navigation):

```
[Grand Palacio Hotel](/accommodations?id=acc-esp-001)
[Iberia Business Class to Madrid](/flights?id=flt-esp-003)
[Private Douro Valley Winery Tour](/experiences?id=exp-esp-002)
```

## Feature Flag Gate

The **Ralph** agent is controlled by the `ralph_agent` Datadog feature flag. When the flag is `false` (default), Ralph is unavailable and Sam will not delegate to him. Toggle the flag in Datadog Feature Management without redeploying.

## Integration

The Tribune concierge is exposed via the backend SSE endpoint:

- **Endpoint**: `POST /api/chat/stream`
- **Auth**: Requires a valid JWT; restricted to Tribune cardholders
- **Streaming**: Server-Sent Events — the frontend renders tokens as they arrive

## File Structure

```
tribune_concierge/
├── __init__.py
├── agent.py              # Sam (coordinator) + sub-agent wiring
└── tools/
    ├── __init__.py
    ├── jenny.py           # Flight search tools
    ├── marcus.py          # Accommodation search tools
    ├── sofia.py           # Itinerary / attraction tools
    ├── luca.py            # Restaurant tools
    ├── ralph.py           # Ralph experimental tools
    ├── flights.py         # Shared flight data helpers
    ├── accommodations.py  # Shared accommodation data helpers
    ├── restaurants.py     # Shared restaurant data helpers
    ├── attractions.py     # Shared experience/attraction data helpers
    ├── api_client.py      # Internal API client for data fetching
    └── utils.py           # Shared utilities
```

## Adding a New Agent

1. Create tools in `tribune_concierge/tools/<agent_name>.py`
2. Define the agent in `tribune_concierge/agent.py` and add it to `root_agent.sub_agents`
3. Update agent transfer messages in `backend/main.py` if needed
4. (Optional) Gate the agent behind a new Datadog feature flag in `backend/feature_flags/__init__.py`
