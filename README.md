# Meridian Credit Card Platform - GCP Agentic Demo

A full-stack credit card platform featuring AI-powered concierge services using Google ADK (Agent Development Kit). The platform offers two tiers of concierge services: Legionnaire (basic chat) and Tribune (premium AI team with specialized agents).

## Features

- **Two-Tier Concierge System**
  - **Legionnaire Concierge**: 24/7 AI chat support for basic concierge services
  - **Tribune AI Concierge Team**: Premium multi-agent system with specialized travel planning agents

- **Voice-to-Text Integration**: Voice input support using Google Cloud Speech-to-Text

- **User Authentication**: JWT-based authentication system

- **Card Applications**: Apply for Legionnaire or Tribune credit cards

- **Benefits Portal**: Comprehensive benefits information for cardholders

## Architecture Overview

```
┌─────────────────┐         ┌──────────────────┐
│                 │         │                  │
│  React Frontend │◄────────┤  FastAPI Backend │
│  (Port 5173)    │   SSE   │  (Port 8000)     │
│                 │         │                  │
└─────────────────┘         └────────┬─────────┘
                                     │
                    ┌────────────────┴──────────────────┐
                    │                                   │
           ┌────────▼──────────┐           ┌───────────▼─────────┐
           │  Tribune Premium  │           │ Legionnaire Basic   │
           │  (Multi-Agent)    │           │  (Single Agent)     │
           └────────┬──────────┘           └─────────────────────┘
                    │
             ┌──────▼───────┐
             │     Sam      │
             │(Coordinator) │
             └──────┬───────┘
                    │
    ┌───────────────┼───────────────┐
    │               │               │
┌───▼───┐     ┌─────▼────┐    ┌────▼────┐
│ Jenny │     │  Marcus  │    │  Sofia  │
│(Flight│     │ (Hotels) │    │(Itiner.)│
└───────┘     └──────────┘    └─────────┘
    │               │
┌───▼───┐     ┌─────▼────┐
│ Luca  │     │   Alex   │
│(Dining│     │ (Budget) │
└───────┘     └──────────┘
```

## Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **Google ADK**: Agent Development Kit for building AI agents
- **Google Generative AI**: Gemini models for conversational AI
- **Google Cloud Speech-to-Text**: Voice transcription service
- **Datadog LLM Observability**: Monitoring and tracing for LLM applications
- **Python 3.10+**

### Frontend
- **React 18**: UI library
- **TypeScript**: Type-safe JavaScript
- **React Router**: Client-side routing
- **Vite**: Build tool and dev server

## Quick Start

### 1. Install Dependencies

```bash
# Python dependencies for backend
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
cd ..

# Node.js dependencies for frontend
cd frontend
npm install
cd ..
```

### 2. Configure Environment

**Backend (.env in backend/ directory):**
```bash
GOOGLE_API_KEY=your_google_api_key
GOOGLE_GENAI_MODEL=gemini-2.0-flash-exp
DATADOG_API_KEY=your_datadog_api_key
DD_SITE=datadoghq.com
ENV=development
JWT_SECRET_KEY=your_secret_key_here
```

**Frontend (.env in frontend/ directory):**
```bash
VITE_API_URL=http://localhost:8000
```

### 3. Start the Backend

```bash
cd backend
python main.py
```

The backend will start on `http://localhost:8000`
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

### 4. Start the Frontend

In a new terminal:

```bash
cd frontend
npm run dev
```

The frontend will start on `http://localhost:5173`

### 5. Test the Application

1. Open your browser to http://localhost:5173
2. Log in with mock user credentials (see Mock Users section)
3. Navigate to the Concierge page
4. Select Tribune or Legionnaire tier based on your card type
5. Start chatting!

---

## API Documentation

### Base URL
```
http://localhost:8000
```

### Authentication

- Google ADK uses API key authentication via `GOOGLE_API_KEY` environment variable
- JWT tokens for user authentication

### Core Endpoints

#### Health Check
```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "travel-planner"
}
```

#### Root
```http
GET /
```

**Response:**
```json
{
  "message": "Travel Planner API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

### Authentication Endpoints

#### Login
```http
POST /api/auth/login
Content-Type: application/json
```

**Request Body:**
```json
{
  "username": "john_tribune",
  "password": "password123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": "1",
    "username": "john_tribune",
    "email": "john@example.com",
    "card_type": "tribune"
  }
}
```

**Error Response (401 Unauthorized):**
```json
{
  "detail": "Invalid username or password"
}
```

#### Get Current User
```http
GET /api/auth/me
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "id": "1",
  "username": "john_tribune",
  "email": "john@example.com",
  "card_type": "tribune"
}
```

**Error Response (401 Unauthorized):**
```json
{
  "detail": "Missing or invalid authorization header"
}
```

### Card Application Endpoints

#### Apply for Card
```http
POST /api/cards/apply
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "card_type": "tribune",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "annual_income": 150000
}
```

**Response (200 OK):**
```json
{
  "application_id": "app_01HQZX...",
  "status": "approved",
  "card_type": "tribune",
  "created_at": "2024-01-08T12:00:00Z"
}
```

### Chat Endpoints

#### Tribune Premium Chat (Multi-Agent)
```http
POST /api/chat/stream
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "I need to plan a trip to Paris",
  "session_id": "session_abc123"
}
```

**Response:** Server-Sent Events (text/event-stream)

**Event Types:**

1. **agent_transfer** - Agent handoff notification
```
data: {"type":"agent_transfer","data":{"agent":"Jenny","message":"Transferring you to Jenny, our flight specialist. She'll help you find the best flights! ✈️"}}
```

2. **content** - Streaming text content
```
data: {"type":"content","data":{"text":"Hello! I'd be happy to help you plan your trip to Paris..."}}
```

3. **done** - Completion signal
```
data: {"type":"done","data":{"message":"Response complete"}}
```

4. **error** - Error notification
```
data: {"type":"error","data":{"message":"An error occurred","detail":"Stack trace..."}}
```

#### Legionnaire Basic Chat (Single Agent)
```http
POST /api/chat/legionnaire/stream
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "Can you recommend a restaurant?",
  "session_id": "session_xyz789"
}
```

**Response:** Server-Sent Events (text/event-stream)

Same event structure as Tribune chat, but without agent_transfer events since there's only one agent.

### Speech-to-Text Endpoint

#### Transcribe Audio
```http
POST /api/speech-to-text
Content-Type: multipart/form-data
```

**Request:** multipart/form-data
- **audio** (file): Audio file in webm/opus format

**Response (200 OK):**
```json
{
  "text": "I need help planning a trip to Tokyo"
}
```

**Response (No Speech):**
```json
{
  "text": "",
  "message": "No speech detected"
}
```

**Error Response (500):**
```json
{
  "detail": "Speech-to-text error: [error message]"
}
```

---

## Agent System

### Tribune Premium (Multi-Agent System)
Located in `travel_planner/agent.py`

- **Sam** 🌟 - Main coordinator who understands your needs
- **Jenny** ✈️ - Flight search specialist
- **Marcus** 🏨 - Accommodation booking expert
- **Sofia** 🗺️ - Itinerary planning & attractions specialist
- **Luca** 🍽️ - Restaurant recommendations specialist
- **Alex** 💰 - Budget management expert

### Legionnaire Basic (Single Agent)
Located in `legionnaire_concierge/agent.py`

- **Concierge** 💬 - General-purpose AI assistant for basic concierge services

---

## Testing

### Run Backend Tests

```bash
cd backend
pytest test_api.py -v
```

**Test Coverage:**
- ✅ Health check endpoint
- ✅ Authentication (login, token validation)
- ✅ Card application
- ✅ Tribune chat streaming
- ✅ Legionnaire chat streaming
- ✅ Speech-to-text (including integration test with real Google API credentials)
- ✅ CORS configuration

**Note on Speech-to-Text Test:**
The `test_speech_to_text_with_valid_audio` test makes a real API call to Google Cloud Speech-to-Text using credentials from your `.env` file. This test:
- Verifies the API integration works correctly
- Uses actual `GOOGLE_API_KEY` authentication
- Creates a valid audio file and tests transcription
- Gracefully skips if the Speech-to-Text API is not enabled on your Google Cloud project

### Test Results Example
```
test_api.py::TestHealthEndpoint::test_health_check PASSED
test_api.py::TestAuthEndpoints::test_login_with_valid_credentials PASSED
test_api.py::TestAuthEndpoints::test_get_me_with_valid_token PASSED
test_api.py::TestTribuneChatEndpoint::test_tribune_chat_stream_endpoint_exists PASSED
test_api.py::TestLegionnaireChatEndpoint::test_legionnaire_chat_stream_endpoint_exists PASSED
test_api.py::TestSpeechToTextEndpoint::test_speech_to_text_with_valid_audio SKIPPED (or PASSED)
==================== 18 passed, 1 skipped, 8 warnings ====================
```

---

## Project Structure

```
gcp-agentic-demo/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── test_api.py            # API endpoint tests
│   ├── test_agent.py          # Agent behavior tests
│   ├── requirements.txt        # Python dependencies
│   ├── models/                 # Pydantic models
│   │   ├── auth.py
│   │   ├── user.py
│   │   └── application.py
│   ├── routers/               # API route handlers
│   │   ├── auth.py
│   │   └── cards.py
│   ├── services/              # Business logic
│   │   ├── auth_service.py
│   │   └── user_service.py
│   └── .env                    # Environment variables
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── Chat.tsx
│   │   │   ├── ChatInput.tsx
│   │   │   ├── ChatMessage.tsx
│   │   │   ├── Header.tsx
│   │   │   └── PreviewModal.tsx
│   │   ├── pages/            # Page components
│   │   │   ├── Home.tsx
│   │   │   ├── Login.tsx
│   │   │   ├── Cards.tsx
│   │   │   ├── Benefits.tsx
│   │   │   ├── Concierge.tsx
│   │   │   ├── Account.tsx
│   │   │   └── Apply.tsx
│   │   ├── utils/            # Utility functions
│   │   │   ├── api.ts
│   │   │   └── auth.ts
│   │   └── types/            # TypeScript types
│   │       ├── chat.ts
│   │       └── user.ts
│   ├── package.json
│   └── .env
├── travel_planner/
│   ├── agent.py              # Tribune multi-agent system
│   └── tools/                # Agent tools
│       ├── jenny.py          # Flight tools
│       ├── marcus.py         # Accommodation tools
│       ├── sofia.py          # Itinerary tools
│       ├── luca.py           # Restaurant tools
│       └── alex.py           # Budget tools
├── legionnaire_concierge/
│   ├── agent.py              # Legionnaire single agent
│   └── __init__.py
├── docker-compose.yml
└── README.md
```

---

## Mock Users

For testing purposes, the following mock users are available:

| Username | Password | Card Type | Email |
|----------|----------|-----------|-------|
| `john_tribune` | `password123` | Tribune | john@example.com |
| `jane_legionnaire` | `password123` | Legionnaire | jane@example.com |
| `bob_none` | `password123` | None | bob@example.com |

---

## Environment Variables

### Backend

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GOOGLE_API_KEY` | Google Cloud API key | Yes | - |
| `GOOGLE_GENAI_MODEL` | Gemini model name | Yes | `gemini-2.0-flash-exp` |
| `DATADOG_API_KEY` | Datadog API key for observability | No | - |
| `DD_SITE` | Datadog site | No | `datadoghq.com` |
| `ENV` | Environment name | No | `development` |
| `JWT_SECRET_KEY` | Secret key for JWT tokens | Yes | - |

### Frontend

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `VITE_API_URL` | Backend API URL | No | `http://localhost:8000` |

---

## Troubleshooting

### Backend won't start
- Check that port 8000 is available
- Verify your `.env` file has the required `GOOGLE_API_KEY` variable
- Make sure all Python dependencies are installed
- Activate virtual environment: `source .venv/bin/activate`

### Frontend shows connection error
- Verify the backend is running on port 8000
- Check the `VITE_API_URL` in `frontend/.env`
- Look for CORS errors in the browser console

### Agents not responding
- Check the backend logs for errors
- Verify your Google API credentials are correct
- Ensure the Google ADK is properly installed
- Check that `GOOGLE_GENAI_MODEL` is set correctly

### Voice input not working
- Ensure microphone permissions are granted in the browser
- Check that `GOOGLE_API_KEY` has Speech-to-Text API enabled
- Verify audio is being captured (check browser console for errors)

---

## Development

### Adding New Agents

To add a new agent to the Tribune system:

1. Create agent tools in `travel_planner/tools/`
2. Define the agent in `travel_planner/agent.py`
3. Add the agent to the `root_agent.sub_agents` list
4. Update the agent transfer messages in `backend/main.py`

### Adding New API Endpoints

1. Create route handler in `backend/routers/`
2. Include router in `backend/main.py`
3. Add tests in `backend/test_api.py`
4. Update API documentation in this README

### Frontend Development

```bash
cd frontend
npm run dev
# Make changes to src/ files
# Vite will hot-reload automatically
```

### Backend Development

```bash
cd backend
python main.py
# Make changes to *.py files
# Server will auto-reload with uvicorn --reload
```

---

## Deployment

### Using Docker Compose

```bash
docker-compose up -d
```

This will start both the backend and frontend services.

### Production Deployment

For production deployment:

1. Update CORS origins in `backend/main.py`
2. Set `VITE_API_URL` to your production backend URL
3. Build the frontend: `cd frontend && npm run build`
4. Deploy the backend with a production ASGI server (e.g., Gunicorn with Uvicorn workers)
5. Serve the frontend `dist/` folder from a CDN or static host

---

## Monitoring

The application includes Datadog LLM Observability for monitoring:
- Agent interactions
- Tool calls
- Response times
- Error rates
- User sessions

Enable by setting `DATADOG_API_KEY` in environment variables.

---

## API Documentation (Interactive)

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## License

Proprietary - Meridian Financial Services

---

## Support

For questions or issues, please contact the development team.

---

Happy Travel Planning! 🌍✈️
