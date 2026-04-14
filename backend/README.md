# Meridian Backend API

FastAPI service powering the Meridian travel platform. Handles authentication, travel data, AI concierge streaming, voice WebSocket connections, and Datadog feature flag evaluation.

## Features

- **Server-Sent Events (SSE)**: Real-time streaming of agent responses to the frontend
- **Datadog APM + LLM Observability**: All requests and agent interactions are traced
- **Remote Feature Flags**: Datadog-backed flags evaluated at runtime via `DD_EXPERIMENTAL_FLAGGING_PROVIDER_ENABLED`
- **JWT Authentication**: Stateless auth with membership-tier enforcement
- **Travel Data API**: JSON-backed endpoints for flights, accommodations, restaurants, and experiences

## API Endpoints

### Auth

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/auth/login` | Log in, returns JWT |
| `GET` | `/api/auth/me` | Current user profile |

### Cards

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/cards/apply` | Apply for a Legionnaire or Tribune card |

### Concierge Chat

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/chat/stream` | Tribune multi-agent chat (SSE) |
| `POST` | `/api/chat/legionnaire/stream` | Legionnaire single-agent chat (SSE) |
| `WS` | `/ws/voice` | Voice conversation via Gemini Live API |

### Travel Data

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/flights` | Browse flights |
| `POST` | `/api/flights/{id}/purchase` | Purchase a flight |
| `GET` | `/api/accommodations` | Browse accommodations |
| `POST` | `/api/accommodations/{id}/book` | Book an accommodation |
| `GET` | `/api/travel/restaurants` | Browse restaurants |
| `POST` | `/api/travel/restaurants/{id}/reserve` | Make a restaurant reservation |
| `GET` | `/api/travel/experiences` | Browse experiences |
| `POST` | `/api/travel/experiences/{id}/reserve` | Reserve an experience |

### Utility

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/health` | Health check |
| `GET` | `/docs` | Interactive API docs (Swagger UI) |

## Feature Flags

Feature flags are defined in `feature_flags/__init__.py` and evaluated via the Datadog SDK at request time. No redeployment is needed to toggle them.

```python
# feature_flags/__init__.py
INSECURE_PROFILE_AGENT = "insecure_profile_agent"
RALPH_AGENT = "ralph_agent"

FLAGS: dict[str, bool] = {
    INSECURE_PROFILE_AGENT: False,   # fallback if flag unavailable
    RALPH_AGENT: False,
}
```

To add a new flag: add an entry to `FLAGS` with a safe default, then evaluate it in the relevant router or service with `ddtrace.contrib.flagging`.

Required env vars for remote flags:
- `DD_EXPERIMENTAL_FLAGGING_PROVIDER_ENABLED=true`
- `DD_REMOTE_CONFIG_ENABLED=true`
- `DD_API_KEY=<your-key>`

## Observability

The backend runs under `ddtrace-run` (see `Dockerfile`) with:

| Signal | Config |
|--------|--------|
| APM traces | Auto-instrumented FastAPI, httpx, sqlalchemy |
| LLM Observability | `DD_LLMOBS_ENABLED=1`, ML app: `travel-planner` |
| Log injection | `DD_LOGS_INJECTION=true` — trace/span IDs in every log line |
| Profiling | `DD_PROFILING_ENABLED=true` |
| Runtime metrics | `DD_RUNTIME_METRICS_ENABLED=true` |

## Running Locally

```bash
# From the project root (with .venv active)
cd backend
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API: http://localhost:8000 — Docs: http://localhost:8000/docs

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_GENAI_MODEL` | Gemini model for agents | Yes |
| `GOOGLE_GENAI_USE_VERTEXAI` | Use Vertex AI | Yes |
| `GOOGLE_APPLICATION_CREDENTIALS` | GCP service account JSON path | Yes |
| `GOOGLE_CLOUD_PROJECT` | GCP project ID | Yes |
| `GOOGLE_CLOUD_LOCATION` | GCP region | Yes |
| `GOOGLE_GENAI_LIVE_MODEL` | Gemini Live model for voice | Yes |
| `JWT_SECRET_KEY` | JWT signing secret | Yes |
| `DATADOG_API_KEY` | Datadog API key | No |
| `DD_ENV` | Datadog environment tag | No |

## File Structure

```
backend/
├── main.py                # FastAPI app, startup, middleware
├── Dockerfile
├── requirements.txt
├── test_api.py            # pytest integration tests
├── data/                  # JSON seed data
│   ├── users.json
│   ├── flights.json
│   ├── accommodations.json
│   ├── restaurants.json
│   └── experiences.json
├── feature_flags/         # Datadog feature flag registry
│   └── __init__.py
├── models/                # Pydantic request/response models
│   ├── auth.py
│   ├── user.py
│   ├── travel.py
│   └── application.py
├── routers/               # Route handlers
│   ├── auth.py
│   ├── cards.py
│   ├── travel.py
│   ├── flights.py
│   └── accommodations.py
└── services/              # Business logic
    ├── auth_service.py
    ├── user_service.py
    ├── travel_service.py
    └── application_service.py
```

## Testing

```bash
cd backend
pytest test_api.py -v
```
