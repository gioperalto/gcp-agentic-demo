# Travel Planner

An all-in-one concierge experience for planning trips from flights to accommodations, itinerary, and even budget.

## Architecture Overview

```
┌─────────────────┐         ┌──────────────────┐
│                 │         │                  │
│  React Frontend │◄────────┤  FastAPI Backend │
│  (Port 5173)    │   SSE   │  (Port 8000)     │
│                 │         │                  │
└─────────────────┘         └────────┬─────────┘
                                     │
                                     │
                            ┌────────▼──────────┐
                            │                   │
                            │  Google ADK       │
                            │  Agent System     │
                            │                   │
                            └────────┬──────────┘
                                     │
                                     │
                             ┌───────▼────────┐
                             │      Sam       │
                             │ (Coordination) │
                             └────────┬───────┘
                                      │
                    ┌─────────────────┼──────────────┐
                    │                 │              │
            ┌───────▼───────┐  ┌──────▼──────┐  ┌────▼──────┐
            │    Jenny      │  │   Marcus    │  │   Sofia   │
            │   (Flights)   │  │(Accommod.)  │  │(Itinerary)│
            └───────────────┘  └─────────────┘  └───────────┘
                                                      │
                                                ┌─────▼─────┐
                                                │   Alex    │
                                                │  (Budget) │
                                                └───────────┘
```

## Quick Start

### 1. Install Dependencies

```bash
# Python dependencies for backend
pip install -r requirements.txt

# Node.js dependencies for frontend
cd frontend && npm install && cd ..
```

### 2. Configure Environment

```bash
# Backend configuration
cd travel_planner
cp .env.example .env
# Edit .env and add your GOOGLE_GENAI_MODEL and DATADOG_API_KEY

# Frontend configuration (optional)
cd ../frontend
cp .env.example .env
# Default VITE_API_URL=http://localhost:8000 should work
```

### 3. Start the Backend

```bash
# From project root
cd backend
python main.py
```

The backend will start on `http://localhost:8000`

- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

### 4. Start the Frontend

In a new terminal:

```bash
# From project root
cd frontend
npm run dev
```

The frontend will start on `http://localhost:5173`

### 5. Test the Application

1. Open your browser to http://localhost:5173
2. You should see the Travel Planner chat interface
3. Type a message like "I need a flight to Paris next week"
4. Watch as Sam transfers you to Jenny, the flight specialist!

## Agent Team

- **Sam** 🌟 - Main coordinator who understands your needs
- **Jenny** ✈️ - Flight search specialist
- **Marcus** 🏨 - Accommodation booking expert
- **Sofia** 🗺️ - Itinerary planning specialist
- **Alex** 💰 - Budget management expert

## Features

✅ **Real-time Streaming** - See responses as they're generated
✅ **Agent Transfers** - Smooth handoffs between specialists with notifications
✅ **Named Agents** - Each agent has a personality and specialty
✅ **Modern UI** - Clean, responsive interface with smooth animations
✅ **SSE Technology** - Server-Sent Events for efficient streaming

## Troubleshooting

### Backend won't start
- Check that port 8000 is available
- Verify your `.env` file has the required `GOOGLE_GENAI_MODEL` variable
- Make sure all Python dependencies are installed

### Frontend shows connection error
- Verify the backend is running on port 8000
- Check the `VITE_API_URL` in `frontend/.env`
- Look for CORS errors in the browser console

### Agents not responding
- Check the backend logs for errors
- Verify your Google API credentials are correct
- Ensure the Google ADK is properly installed

## Development

### Backend Development
```bash
cd backend
# Make changes to main.py
# Server will auto-reload with uvicorn --reload
```

### Frontend Development
```bash
cd frontend
# Make changes to src/ files
# Vite will hot-reload automatically
```

## Next Steps

- Try different queries to interact with various specialists
- Explore the API documentation at http://localhost:8000/docs
- Customize agent personalities in `travel_planner/agent.py`
- Modify the UI styling in `frontend/src/components/*.css`

## Production Deployment

For production deployment:

1. Update CORS origins in `backend/main.py`
2. Set `VITE_API_URL` to your production backend URL
3. Build the frontend: `cd frontend && npm run build`
4. Deploy the backend with a production ASGI server
5. Serve the frontend `dist/` folder from a CDN or static host

---

Happy Travel Planning! 🌍✈️
