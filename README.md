# Meridian — Travel & Hospitality

A full-stack travel platform featuring AI-powered concierge services built with Google ADK (Agent Development Kit). Meridian helps travelers discover flights, accommodations, restaurants, and experiences through two tiers of AI concierge: Legionnaire (personal chat assistant) and Tribune (premium multi-agent travel team).

## Features

- **AI Concierge Services**
  - **Legionnaire Concierge**: 24/7 AI chat assistant for affordable travel recommendations
  - **Tribune AI Travel Team**: Premium multi-agent system with specialized travel planning agents

- **Voice Integration**: Real-time bidirectional voice via Gemini Live API (Tribune members only)

- **Travel Discovery**: Browse and book flights, accommodations, restaurants, and local experiences across 6 countries

- **User Authentication**: JWT-based authentication with membership tiers

- **Membership Cards**: Apply for Legionnaire or Tribune membership cards with tiered credit limits and reward points

- **Feature Flags**: Datadog-backed remote feature flags control agent availability and load generation

- **Load Generation**: Automated Playwright-based traffic simulation instrumented with Datadog APM

- **Observability**: Datadog LLM Observability, APM, RUM, logs, and CSPM via Docker Compose

## Architecture Overview

```
┌─────────────────┐         ┌──────────────────┐       ┌──────────────────┐
│                 │         │                  │       │  Datadog         │
│  React Frontend │◄────────┤  FastAPI Backend │──────►│  APM / LLM Obs   │
│  (Port 5173)    │   SSE   │  (Port 8000)     │       │  RUM / Logs      │
│                 │         │                  │       └──────────────────┘
└─────────────────┘         └────────┬─────────┘
         ▲                           │
         │                ┌──────────┴─────────────────┐
┌────────┴───────┐         │                           │
│  Load Gen      │  ┌──────▼────────────┐   ┌──────────▼──────────┐
│  (Playwright)  │  │  Tribune Premium  │   │  Legionnaire Basic  │
│  DD APM traces │  │  (Multi-Agent)    │   │  (Single Agent)     │
└────────────────┘  └──────┬────────────┘   └─────────────────────┘
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
       └───┬───┘     └──────────┘    └─────────┘
           │
       ┌───▼───┐
       │ Luca  │
       │(Dining│
       └───────┘
```

## Services

| Directory | Description | README |
|-----------|-------------|--------|
| `backend/` | FastAPI API, data, routers, feature flags | [backend/README.md](backend/README.md) |
| `frontend/` | React + TypeScript + Vite SPA | [frontend/README.md](frontend/README.md) |
| `tribune_concierge/` | Multi-agent premium travel team | [tribune_concierge/README.md](tribune_concierge/README.md) |
| `legionnaire_concierge/` | Single-agent budget concierge | [legionnaire_concierge/README.md](legionnaire_concierge/README.md) |
| `load-gen/` | Playwright load generator with Datadog APM | [load-gen/README.md](load-gen/README.md) |

## Tech Stack

### Backend
- **FastAPI**: Web framework with SSE streaming
- **Google ADK**: Agent Development Kit for building AI agents
- **Google Vertex AI**: Gemini models for conversational AI
- **Gemini Live API**: Real-time bidirectional voice conversations
- **Datadog ddtrace**: LLM Observability, APM, log injection, and remote feature flags
- **Python 3.10+**

### Frontend
- **React 18 + TypeScript**: UI library
- **Vite**: Build tool and dev server with HMR
- **Datadog Browser SDK**: Real User Monitoring (RUM)

### Load Generator
- **Playwright**: Browser automation for realistic user sessions
- **ddtrace**: APM traces correlated with backend spans
- **Datadog Feature Flags**: `load-gen-enabled` flag gates load generation remotely

---

## Quick Start (Docker Compose)

The recommended way to run the full stack is via Docker Compose — it starts the backend, frontend, Datadog agent, and load generator together.

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- A GCP service account JSON file with Vertex AI access
- A [Datadog API key](https://app.datadoghq.com/organization-settings/api-keys) for observability and feature flags

### 1. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

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
# Datadog RUM (optional, for frontend observability)
VITE_DD_APP_ID=your-dd-app-id
VITE_DD_CLIENT_TOKEN=your-dd-client-token
VITE_DD_SITE=datadoghq.com
```

`GOOGLE_APPLICATION_CREDENTIALS` must be an **absolute path** to the service account JSON on your host — Docker Compose mounts it into the container automatically.

### 2. Build and Start

```bash
docker compose up --build
```

This starts four services:

| Service | URL | Description |
|---------|-----|-------------|
| **frontend** | http://localhost:5173 | React app (Vite dev server) |
| **backend** | http://localhost:8000 | FastAPI with ddtrace APM |
| **dd-agent** | localhost:8125/udp, :8126/tcp | Datadog Agent (logs, APM, CSPM) |
| **load-gen** | — | Playwright traffic simulator |

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
- **Load Gen**: Edit files in `load-gen/` — restart the container to pick up changes

### 5. Stop

```bash
docker compose down
```

---

## Quick Start (Local — without Docker)

### 1. Install Dependencies

```bash
# Python dependencies (backend + agents)
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Node.js dependencies (frontend)
cd frontend && npm install && cd ..
```

### 2. Start the Backend

```bash
cd backend
python main.py
```

Backend: http://localhost:8000 — API docs at http://localhost:8000/docs

### 3. Start the Frontend

```bash
cd frontend
npm run dev
```

Frontend: http://localhost:5173

---

## Mock Users

| Username | Password | Membership | Credit Limit | Reward Multiplier |
|----------|----------|------------|-------------|-------------------|
| `demo_user` | `password123` | Legionnaire | $15,000 | 1.0x |
| `wealthy_user` | `password123` | Tribune | $50,000 | 2.5x |
| `young_user` | `password123` | None | — | — |

---

## Feature Flags

Feature flags are managed via **Datadog Feature Management** and evaluated remotely by the backend at runtime using `DD_EXPERIMENTAL_FLAGGING_PROVIDER_ENABLED`. No redeployment is needed to toggle them.

| Flag Key | Default | Description |
|----------|---------|-------------|
| `insecure_profile_agent` | `false` | Enables the insecure profile agent (demo/security testing only) |
| `ralph_agent` | `false` | Enables the Ralph experimental agent |
| `load-gen-enabled` | `true` | Gates whether the load generator runs sessions |

The flag registry lives in `backend/feature_flags/__init__.py`. Add new flags there — one entry per flag with its default fallback value.

See the [Datadog Feature Management docs](https://docs.datadoghq.com/service_management/feature_management/) for setup.

---

## Observability (Datadog)

All services ship telemetry to the Datadog Agent container (`dd-agent`) running in the same Docker network.

| Signal | Service(s) | Details |
|--------|-----------|---------|
| **APM traces** | backend, load-gen | `ddtrace-run` auto-instruments FastAPI and Playwright sessions |
| **LLM Observability** | backend | Agent interactions traced via `DD_LLMOBS_ENABLED=1` under ML app `travel-planner` |
| **Logs** | all | JSON logs with trace/span ID injection for correlated log-to-trace links |
| **RUM** | frontend | Browser SDK tracks page views, actions, and errors |
| **CSPM** | dd-agent | Cloud Security Posture Management enabled |
| **Remote Config** | backend | Powers feature flag evaluation (`DD_REMOTE_CONFIGURATION_ENABLED=true`) |

Unified service tagging (`env`, `service`, `version`) is applied via Docker labels and environment variables so all signals are correlated in Datadog.

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DD_ENV` | Datadog environment tag | No (default: `dev`) |
| `DATADOG_API_KEY` | Datadog API key | No (observability disabled without it) |
| `GOOGLE_GENAI_MODEL` | Gemini model name | Yes |
| `GOOGLE_GENAI_USE_VERTEXAI` | Use Vertex AI endpoints | Yes |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to GCP service account JSON | Yes |
| `GOOGLE_CLOUD_PROJECT` | GCP project ID | Yes |
| `GOOGLE_CLOUD_LOCATION` | GCP region | Yes |
| `GOOGLE_GENAI_LIVE_MODEL` | Gemini Live model for voice | Yes |
| `JWT_SECRET_KEY` | Secret key for JWT tokens | Yes |
| `VITE_API_URL` | Backend API URL for the frontend | No (default: `http://localhost:8000`) |
| `VITE_DD_APP_ID` | Datadog RUM application ID | No |
| `VITE_DD_CLIENT_TOKEN` | Datadog RUM client token | No |
| `VITE_DD_SITE` | Datadog site (e.g. `datadoghq.com`) | No |

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

Interactive API docs: http://localhost:8000/docs

---

## Project Structure

```
meridian/
├── backend/                        # FastAPI application
│   ├── main.py
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── data/                       # JSON seed data
│   ├── feature_flags/              # Datadog feature flag registry
│   ├── models/                     # Pydantic models
│   ├── routers/                    # API route handlers
│   └── services/                   # Business logic
├── frontend/                       # React + TypeScript SPA
│   ├── Dockerfile
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── utils/
│       └── types/
├── tribune_concierge/              # Tribune multi-agent travel team
│   ├── agent.py
│   └── tools/
├── legionnaire_concierge/          # Legionnaire personal assistant
│   ├── agent.py
│   └── tools.py
├── load-gen/                       # Playwright load generator
│   ├── main.py
│   ├── users.json
│   ├── Dockerfile
│   └── entrypoint.sh
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Testing

```bash
# API integration tests
cd backend
pytest test_api.py -v
```

---

## Troubleshooting

### Docker Compose issues
- `GOOGLE_APPLICATION_CREDENTIALS` must be an absolute path to a file that exists on the host
- If the Datadog agent fails, verify `DATADOG_API_KEY` is set (or remove `dd-agent` to run without observability)
- Run `docker compose logs <service>` to inspect individual service logs

### Backend won't start
- Check port 8000 is free
- Verify all required GCP variables are in `.env`

### Frontend shows connection error
- Verify the backend is running on port 8000
- Check the `VITE_API_URL` value
- Look for CORS errors in the browser console

### Agents not responding
- Check backend logs for Vertex AI errors
- Verify the GCP service account has Vertex AI access
- Ensure `GOOGLE_GENAI_MODEL` is set

### Voice input not working
- Voice is available to Tribune members only
- Grant microphone permissions in the browser
- Check `GOOGLE_GENAI_LIVE_MODEL` is set in `.env`

### Load generator not running
- Check the `load-gen-enabled` feature flag in Datadog Feature Management — the service polls this flag and skips sessions when it is off
- Inspect logs: `docker compose logs load-gen`

---

## License

This project is licensed under the [MIT License](LICENSE).
