# Meridian — Travel & Hospitality

A full-stack travel platform featuring AI-powered concierge services built with Google ADK (Agent Development Kit). Meridian helps travelers discover flights, accommodations, restaurants, and experiences through two tiers of AI concierge: Legionnaire (personal chat assistant) and Tribune (premium multi-agent travel team).

## Features

- **AI Concierge Services**
  - **Legionnaire Concierge**: 24/7 AI chat assistant for travel recommendations and support
  - **Tribune AI Travel Team**: Premium multi-agent system with specialized travel planning agents

- **Voice Integration**: Real-time bidirectional voice via Gemini Live API (Tribune members only)

- **Travel Discovery**: Browse and book flights, accommodations, restaurants, and local experiences

- **User Authentication**: JWT-based authentication system

- **Membership Tiers**: Apply for Legionnaire or Tribune membership cards with tiered benefits

- **Benefits Portal**: Comprehensive benefits and rewards information for members

- **Observability**: Datadog LLM Observability, APM, logs, and CSPM via Docker Compose

## Architecture Overview

```
┌─────────────────┐         ┌──────────────────┐       ┌──────────────┐
│                 │         │                  │       │  Datadog     │
│  React Frontend │◄────────┤  FastAPI Backend │──────►│  Agent       │
│  (Port 5173)    │   SSE   │  (Port 8000)     │       │  (APM/Logs)  │
│                 │         │                  │       └──────────────┘
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
    │
┌───▼───┐
│ Luca  │
│(Dining│
└───────┘
```

## Tech Stack

### Backend
- **FastAPI**: Web framework for building APIs
- **Google ADK**: Agent Development Kit for building AI agents
- **Google Vertex AI**: Gemini models for conversational AI
- **Gemini Live API**: Real-time bidirectional voice conversations
- **Datadog**: LLM Observability, APM, and log monitoring
- **Python 3.10+**

### Frontend
- **React 18**: UI library
- **TypeScript**: Type-safe JavaScript
- **React Router**: Client-side routing
- **Vite**: Build tool and dev server

---

## Quick Start (Docker Compose)

The recommended way to run the full stack (backend, frontend, and Datadog agent) is via Docker Compose.

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- A GCP service account JSON file with Vertex AI access
- (Optional) A [Datadog API key](https://app.datadoghq.com/organization-settings/api-keys) for observability

### 1. Configure Environment

Copy the example env file and fill in your values:

```bash
cp .env.example .env
```

Edit `.env` with your actual credentials:

```bash
DD_ENV=dev
DATADOG_API_KEY=your-datadog-api-key
GOOGLE_GENAI_MODEL=gemini-3-flash-preview
GOOGLE_GENAI_USE_VERTEXAI=True
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account.json
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_GENAI_LIVE_MODEL=gemini-live-2.5-flash-native-audio
GOOGLE_CLOUD_LOCATION=us-central1
JWT_SECRET_KEY=change-me-in-production
VITE_API_URL=http://localhost:8000
```

`GOOGLE_APPLICATION_CREDENTIALS` must be an **absolute path** to the service account JSON file on your host machine. Docker Compose mounts it into the container automatically.

### 2. Build and Start

```bash
docker compose up --build
```

This starts three services:

| Service | URL | Description |
|---------|-----|-------------|
| **frontend** | http://localhost:5173 | React app (Vite dev server) |
| **backend** | http://localhost:8000 | FastAPI (with ddtrace APM) |
| **dd-agent** | localhost:8125/udp, :8126/tcp | Datadog Agent (logs, APM, CSPM) |

### 3. Verify

```bash
# Backend health check
curl http://localhost:8000/api/health
# → {"status":"healthy","service":"travel-planner"}

# Frontend
open http://localhost:5173
```

### 4. Hot Reload (Development)

Source directories are volume-mounted for live reloading:

- **Backend**: Edit files in `backend/`, `tribune_concierge/`, or `legionnaire_concierge/` — uvicorn auto-reloads
- **Frontend**: Edit files in `frontend/src/` — Vite HMR updates the browser instantly

### 5. Stop

```bash
docker compose down
```

---

## Quick Start (Local — without Docker)

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

Create a `.env` file in the project root (see `.env.example`) with your GCP and Datadog credentials. The backend loads env vars via `dotenv`.

### 3. Start the Backend

```bash
cd backend
python main.py
```

The backend starts on http://localhost:8000
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

### 4. Start the Frontend

In a new terminal:

```bash
cd frontend
npm run dev
```

The frontend starts on http://localhost:5173

---

## Mock Users

For testing purposes, the following mock users are available:

| Username | Password | Membership | Credit Limit | Reward Multiplier |
|----------|----------|------------|-------------|-------------------|
| `demo_user` | `password123` | Legionnaire | $15,000 | 1.0x |
| `wealthy_user` | `password123` | Tribune | $50,000 | 2.5x |
| `young_user` | `password123` | None | — | — |

---

## Environment Variables

All environment variables are consolidated in a single root `.env` file. See `.env.example` for reference.

| Variable | Description | Required |
|----------|-------------|----------|
| `DD_ENV` | Datadog environment tag | No (default: `dev`) |
| `DATADOG_API_KEY` | Datadog API key for observability | No |
| `GOOGLE_GENAI_MODEL` | Gemini model name | Yes |
| `GOOGLE_GENAI_USE_VERTEXAI` | Use Vertex AI endpoints | Yes |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to GCP service account JSON | Yes |
| `GOOGLE_CLOUD_PROJECT` | GCP project ID | Yes |
| `GOOGLE_CLOUD_LOCATION` | GCP region | Yes |
| `GOOGLE_GENAI_LIVE_MODEL` | Gemini Live model for voice | Yes |
| `JWT_SECRET_KEY` | Secret key for JWT tokens | Yes |
| `VITE_API_URL` | Backend API URL for the frontend | No (default: `http://localhost:8000`) |

---

## AI Concierge System

### Tribune Premium (Multi-Agent Travel Team)
Located in `tribune_concierge/agent.py`

- **Sam** — Lead travel coordinator who understands your needs and delegates to specialists
- **Jenny** — Flight search specialist
- **Marcus** — Accommodation booking expert
- **Sofia** — Itinerary planning and local attractions specialist
- **Luca** — Restaurant and dining recommendations specialist

### Legionnaire (Personal Travel Assistant)
Located in `legionnaire_concierge/agent.py`

- **Concierge** — AI travel assistant for general recommendations and support

---

## API Documentation

### Core Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/auth/login` | User login (returns JWT) |
| `GET` | `/api/auth/me` | Current user info |
| `POST` | `/api/cards/apply` | Apply for a membership card |
| `POST` | `/api/chat/stream` | Tribune chat (SSE, multi-agent) |
| `POST` | `/api/chat/legionnaire/stream` | Legionnaire chat (SSE, single agent) |
| `WS` | `/ws/voice` | Voice conversation (Gemini Live API) |

### Travel Data Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/flights` | Browse flights |
| `GET` | `/api/accommodations` | Browse accommodations |
| `GET` | `/api/travel/restaurants` | Browse restaurants |
| `GET` | `/api/travel/experiences` | Browse experiences |

Interactive API docs available at http://localhost:8000/docs when the backend is running.

---

## Project Structure

```
meridian/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── Dockerfile              # Backend container image
│   ├── requirements.txt        # Python dependencies
│   ├── data/                   # JSON seed data
│   │   ├── users.json
│   │   ├── flights.json
│   │   ├── accommodations.json
│   │   ├── restaurants.json
│   │   └── experiences.json
│   ├── models/                 # Pydantic models
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── travel.py
│   │   └── application.py
│   ├── routers/                # API route handlers
│   │   ├── auth.py
│   │   ├── cards.py
│   │   ├── travel.py
│   │   ├── flights.py
│   │   └── accommodations.py
│   ├── services/               # Business logic
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── travel_service.py
│   │   └── application_service.py
│   └── test_api.py             # API tests
├── frontend/
│   ├── Dockerfile              # Frontend container image
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── pages/              # Page components
│   │   │   ├── Flights.tsx
│   │   │   ├── Accommodations.tsx
│   │   │   ├── Restaurants.tsx
│   │   │   ├── Experiences.tsx
│   │   │   ├── Concierge.tsx
│   │   │   └── ...
│   │   ├── utils/
│   │   └── types/
│   ├── package.json
│   └── vite.config.ts
├── tribune_concierge/          # Tribune multi-agent travel team
│   ├── agent.py
│   └── tools/
│       ├── jenny.py            # Flight tools
│       ├── marcus.py           # Accommodation tools
│       ├── sofia.py            # Itinerary tools
│       ├── luca.py             # Restaurant tools
│       └── ...
├── legionnaire_concierge/      # Legionnaire personal assistant
│   └── agent.py
├── docker-compose.yml          # Full stack orchestration
├── .dockerignore
├── .env.example                # Environment variable template
└── README.md
```

---

## Testing

```bash
cd backend
pytest test_api.py -v
```

---

## Monitoring

The Docker Compose setup includes a Datadog Agent with:

- **APM**: Automatic tracing via `ddtrace-run` (backend)
- **Logs**: Container log collection with source/service tagging
- **CSPM**: Cloud Security Posture Management
- **LLM Observability**: Agent interaction tracing

Unified service tagging is applied via env vars, Docker labels, and autodiscovery annotations. Services appear in Datadog as `travel-planner-api` and `travel-planner-frontend`.

---

## Troubleshooting

### Docker Compose issues
- Ensure `GOOGLE_APPLICATION_CREDENTIALS` in `.env` is an absolute path to a file that exists on your host
- If the Datadog agent fails, verify `DATADOG_API_KEY` is set (or remove the `dd-agent` service to run without it)
- Run `docker compose logs <service>` to inspect individual service logs

### Backend won't start
- Check that port 8000 is available
- Verify your `.env` file has all required GCP variables
- Make sure all Python dependencies are installed

### Frontend shows connection error
- Verify the backend is running on port 8000
- Check the `VITE_API_URL` value
- Look for CORS errors in the browser console

### Agents not responding
- Check the backend logs for errors
- Verify your GCP service account has Vertex AI access
- Ensure `GOOGLE_GENAI_MODEL` is set correctly

### Voice input not working
- Voice is available to Tribune members only
- Ensure microphone permissions are granted in the browser
- Check that `GOOGLE_GENAI_LIVE_MODEL` is set in your `.env`

---

## Development

### Adding New Agents

To add a new agent to the Tribune system:

1. Create agent tools in `tribune_concierge/tools/`
2. Define the agent in `tribune_concierge/agent.py`
3. Add the agent to the `root_agent.sub_agents` list
4. Update the agent transfer messages in `backend/main.py`

### Adding New API Endpoints

1. Create route handler in `backend/routers/`
2. Include router in `backend/main.py`
3. Add tests in `backend/test_api.py`

---

## License

This project is licensed under the [MIT License](LICENSE).
