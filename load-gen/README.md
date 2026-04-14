# Load Generator

Simulates realistic user sessions against the Meridian frontend using **Playwright** browser automation. Every session is instrumented with **Datadog APM** (ddtrace) so load-gen traces are correlated with backend traces in the same Datadog service map.

## What It Does

Each simulated session follows a realistic user journey:

1. **Login** — authenticates as a randomly chosen user from `users.json`
2. **Browse** — visits travel pages (flights, accommodations, restaurants, experiences)
3. **Chat** — sends a natural-language travel query to the Legionnaire or Tribune concierge
4. **Pause** — waits a configurable interval before the next session

Sessions run in a loop. By default a single concurrent worker runs sessions ~90 seconds apart (plus up to 30 s of jitter) to produce sporadic, realistic traffic rather than a constant firehose.

## Feature Flag Gate

The load generator checks a **Datadog Feature Flag** before starting each session batch. If the `load-gen-enabled` flag is `false` in Datadog Feature Management the generator sleeps and re-checks after `FLAG_POLL_INTERVAL_SECONDS` (default: 60 s). This lets you pause load generation instantly from the Datadog UI without redeploying.

## Running with Docker Compose

The load generator is included in `docker-compose.yml` and starts automatically:

```bash
docker compose up --build
```

To run only the load generator (after the rest of the stack is up):

```bash
docker compose up load-gen
```

To stop load generation without stopping the rest of the stack:

```bash
docker compose stop load-gen
```

Or disable it remotely by toggling the `load-gen-enabled` flag off in **Datadog > Feature Management**.

## Running Locally

```bash
cd load-gen
pip install -r requirements.txt
playwright install chromium
python main.py
```

The script expects the frontend at `http://localhost:5173` and backend at `http://localhost:8000` by default.

## Configuration

All settings are controlled via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `LOAD_GEN_FRONTEND_URL` | `http://localhost:5173` (or `http://frontend:5173` in Docker) | Frontend URL to drive |
| `LOAD_GEN_BACKEND_URL` | `http://localhost:8000` (or `http://backend:8000` in Docker) | Backend URL for health checks |
| `LOAD_GEN_USERS_FILE` | `users.json` (same directory as `main.py`) | Path to users file |
| `LOAD_GEN_HEADLESS` | `true` | Run Chromium headlessly (`false` shows the browser window) |
| `LOAD_GEN_CONCURRENCY` | `1` | Number of parallel browser workers |
| `LOAD_GEN_SESSION_PAUSE_SECONDS` | `90` | Base pause between sessions (jitter added on top) |
| `LOAD_GEN_STEP_DELAY_SECONDS` | `0.5` | Delay between individual page interactions |
| `LOAD_GEN_TIMEOUT_MS` | `60000` | Page/navigation timeout in milliseconds |
| `LOAD_GEN_AGENT_REPLY_TIMEOUT_MS` | `120000` | Timeout waiting for an agent reply |
| `LOAD_GEN_ENABLED_FLAG` | `load-gen-enabled` | Datadog feature flag key that gates execution |
| `LOAD_GEN_FLAG_POLL_INTERVAL_SECONDS` | `60` | How often to re-check the flag when disabled |
| `DD_SERVICE` | `travel-planner-load-gen` | Datadog service name |
| `DD_ENV` | `development` | Datadog environment tag |
| `DD_AGENT_HOST` | `localhost` | Datadog Agent host |

## Observability

- **APM**: Each session is wrapped in a `ddtrace` span (`load_gen.session`) with tags for `user`, `session_id`, and outcome
- **Logs**: Structured JSON logs with injected `dd.trace_id` / `dd.span_id` for log-to-trace correlation in Datadog
- **Service map**: Load-gen appears as `travel-planner-load-gen` calling `travel-planner-api` and `travel-planner-frontend`

## Users File

`users.json` lists the mock accounts the generator picks from at random. Each entry needs at minimum `username` and `password`:

```json
[
  { "username": "demo_user", "password": "password123" },
  { "username": "wealthy_user", "password": "password123" }
]
```

## File Structure

```
load-gen/
├── main.py          # Session runner with Playwright + ddtrace instrumentation
├── users.json       # Mock users for load generation
├── Dockerfile       # Container image (Chromium + Xvfb for non-headless mode)
├── entrypoint.sh    # Starts Xvfb then executes main.py
└── requirements.txt # Python dependencies (playwright, ddtrace)
```
