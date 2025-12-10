# Travel Planner Backend API

FastAPI backend service for the Travel Planner application with real-time streaming support.

## Features

- **Server-Sent Events (SSE)** for real-time streaming of agent responses
- **Agent Transfer Detection** with user-friendly messages
- **Named Agents** with distinct personalities:
  - Sam (Main Coordinator) 🌟
  - Jenny (Flight Specialist) ✈️
  - Marcus (Accommodation Expert) 🏨
  - Sofia (Itinerary Planner) 🗺️
  - Alex (Budget Manager) 💰

## API Endpoints

### `POST /api/chat/stream`

Stream chat responses with Server-Sent Events.

**Request Body:**
```json
{
  "message": "I need a flight to Paris",
  "session_id": "optional-session-id"
}
```

**Response:** SSE stream with events:

- `agent_transfer` - When switching to a specialized agent
  ```json
  {
    "type": "agent_transfer",
    "data": {
      "agent": "Jenny",
      "message": "Transferring you to Jenny, our flight specialist..."
    }
  }
  ```

- `content` - Streaming text tokens
  ```json
  {
    "type": "content",
    "data": {
      "text": "I found some great options..."
    }
  }
  ```

- `done` - Stream completion
  ```json
  {
    "type": "done",
    "data": {
      "message": "Response complete"
    }
  }
  ```

- `error` - Error handling
  ```json
  {
    "type": "error",
    "data": {
      "message": "Error description"
    }
  }
  ```

### `GET /api/health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "travel-planner"
}
```

### `GET /`

Root endpoint with API information.

## Running the Backend

```bash
# From the backend directory
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## Development

- API docs available at `http://localhost:8000/docs`
- Alternative docs at `http://localhost:8000/redoc`

## Environment Variables

Set these in `../travel_planner/.env`:

- `GOOGLE_GENAI_MODEL` - The Google Generative AI model to use
- `DATADOG_API_KEY` - (Optional) For observability with Datadog

## CORS Configuration

Currently configured to allow all origins (`*`). For production, update the `allow_origins` list in `main.py` to include only your frontend domain.
