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

## Production Deployment (GCP with Terraform)

Deploy the full stack to Google Cloud Platform using the included Terraform configuration.

### Architecture

```
                    [Google-Managed SSL Cert]
                              |
                 [Global HTTPS Load Balancer]
                    /                    \
        [Cloud CDN]                [Serverless NEG]
            |                            |
[GCS Bucket: Frontend SPA]     [Cloud Run: Backend]
                                 (FastAPI + ADK Agents)
                                        |
                          ┌─────────────┼──────────────┐
                          │             │              │
                   [Vertex AI]    [Firestore]   [Secret Manager]
                    (Gemini)    (travel data,
                                 users, cards)

[GCS Bucket: Media (private)]
  └── img/accommodations/      ← served via V4 signed URLs
  └── img/restaurants/            generated by backend
  └── img/experiences/
  └── img/flights/
```

- `/*` (default) → Cloud Storage bucket (frontend SPA via CDN)
- `/api/*`, `/ws/*` → Cloud Run backend (FastAPI with ADK agents)
- Images → private GCS media bucket; backend generates time-limited signed URLs

### Prerequisites

- [Terraform](https://developer.hashicorp.com/terraform/install) >= 1.5
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) (`gcloud`)
- A GCP project with billing enabled
- A domain name you control (for DNS + SSL)
- (Optional) GitHub App installation ID for CI/CD triggers

### 1. Configure Variables

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:

```hcl
project_id  = "your-gcp-project-id"
region      = "us-central1"
domain      = "travel.example.com"
environment = "prod"
```

Set secret values via environment variables (never commit these):

```bash
export TF_VAR_jwt_secret_key="your-jwt-secret"
export TF_VAR_datadog_api_key="your-dd-api-key"
export TF_VAR_dd_application_key="your-dd-app-key"
export TF_VAR_vite_dd_client_token="your-dd-client-token"
```

### 2. Deploy Infrastructure

```bash
cd terraform
terraform init
terraform plan    # Review the changes
terraform apply   # Create all resources
```

Terraform creates: Cloud Run service, frontend GCS bucket (public SPA), private media GCS bucket (images), Firestore database, Firestore seeder Cloud Run Job, HTTPS Load Balancer with CDN, DNS zone, Artifact Registry, Secret Manager secrets, service accounts with appropriate IAM bindings, and (optionally) Cloud Build CI/CD triggers.

### 3. Configure DNS

After `terraform apply`, point your domain to the load balancer IP:

```bash
terraform output dns_name_servers
# Add these NS records at your domain registrar
```

Or if using an existing DNS zone, create an A record pointing to:

```bash
terraform output load_balancer_ip
```

### 4. Initial Deployment

**Backend** — build and push the Docker image, then deploy to Cloud Run:

```bash
export AR_REPO=$(terraform -chdir=terraform output -raw artifact_registry_repo)
./scripts/build-and-push.sh v1.0.0
gcloud run deploy $(terraform -chdir=terraform output -raw cloud_run_url | sed 's|https://||;s|\..*||') \
  --image "$AR_REPO/travel-planner-api:v1.0.0" \
  --region us-central1
```

**Frontend** — build the SPA and upload to GCS:

```bash
export DEPLOY_BUCKET=$(terraform -chdir=terraform output -raw frontend_bucket_name)
export VITE_API_BASE_URL="https://your-domain.com"
./scripts/deploy-frontend.sh
```

**Images** — upload travel photos to the private media bucket (see [docs/seeding.md](docs/seeding.md) for details):

```bash
export MEDIA_BUCKET=$(terraform -chdir=terraform output -raw media_bucket_name)
gsutil -m rsync -r -d frontend/public/img gs://${MEDIA_BUCKET}/img
```

**Firestore** — seed the catalog data (runs inside the backend container via Cloud Run Job):

```bash
export SEEDER_JOB=$(terraform -chdir=terraform output -raw seeder_job_name)
gcloud run jobs execute $SEEDER_JOB --region us-central1 --wait
```

> **Note:** Images are not included in the repository — bring your own. See [docs/seeding.md](docs/seeding.md) for the full seeding guide including expected directory structure, IAM setup, and local dev instructions.

### 5. CI/CD (Automatic Deploys)

If you configured the `github_*` variables in `terraform.tfvars`, Cloud Build triggers are created automatically:

- **Push to `main` with `backend/**` changes** → builds Docker image, pushes to Artifact Registry, deploys new Cloud Run revision
- **Push to `main` with `frontend/**` changes** → builds SPA, syncs to GCS, invalidates CDN cache
- **Push to `main` with `backend/data/**`, `frontend/public/img/**`, or `backend/scripts/**` changes** → syncs images to media bucket, executes Firestore seeder job

### 6. Verify

```bash
# Health check
curl https://your-domain.com/api/health
# → {"status":"healthy","service":"travel-planner"}

# Frontend
open https://your-domain.com
```

### Terraform Modules

| Module | Description |
|--------|-------------|
| `project_services` | Enables required GCP APIs (including Firestore, Storage, IAM Credentials) |
| `artifact_registry` | Docker image repository |
| `service_accounts` | Cloud Run SA with Vertex AI, Firestore, Storage, and Secret Manager access |
| `secrets` | Secret Manager for JWT, Datadog keys |
| `cloud_run` | Backend service (3600s timeout, session affinity, internal LB ingress) |
| `frontend_bucket` | Public GCS bucket with SPA routing |
| `media_bucket` | Private GCS bucket for travel images (signed URL access only) |
| `firestore` | Firestore native-mode database for catalog data and user state |
| `seeder_job` | Cloud Run Job that upserts catalog collections from JSON seed files |
| `load_balancer` | Global HTTPS LB + CDN + URL map + HTTP→HTTPS redirect |
| `dns` | Cloud DNS zone + A record |
| `datadog` | Agentless ddtrace env var configuration |
| `cicd` | Cloud Build GitHub triggers (backend + frontend + content seed) |

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
| `MEDIA_BUCKET_NAME` | GCS bucket name for private travel images (signed URL serving) | No (local dev uses static files) |
| `SIGNED_URL_TTL_MINUTES` | TTL for signed image URLs in minutes | No (default: `60`) |

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
│   ├── Dockerfile                  # Backend container image
│   ├── cloudbuild.yaml             # Backend CI/CD pipeline
│   ├── cloudbuild.content.yaml     # Content pipeline (images + Firestore seed)
│   ├── requirements.txt
│   ├── data/                       # JSON source files for Firestore seeding
│   ├── feature_flags/              # Datadog feature flag registry
│   ├── models/                     # Pydantic models
│   ├── repositories/               # Firestore data access layer
│   ├── routers/                    # API route handlers
│   ├── scripts/                    # Operational scripts (seed_firestore.py)
│   └── services/                   # Business logic + Firestore/GCS clients
├── frontend/                       # React + TypeScript SPA
│   ├── Dockerfile                  # Multi-stage prod build (Node → nginx)
│   ├── cloudbuild.yaml             # Frontend CI/CD pipeline
│   ├── nginx.conf                  # SPA routing for production
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── utils/
│       └── types/
├── terraform/
│   ├── main.tf                     # Root module (wires all modules)
│   ├── variables.tf                # Top-level variables
│   ├── outputs.tf                  # LB IP, Cloud Run URL, bucket names
│   ├── terraform.tfvars.example
│   └── modules/
│       ├── project_services/       # Enable required GCP APIs
│       ├── artifact_registry/      # Docker image repo
│       ├── service_accounts/       # Cloud Run SA + IAM bindings
│       ├── secrets/                # Secret Manager secrets
│       ├── cloud_run/              # Backend Cloud Run service
│       ├── frontend_bucket/        # Public GCS bucket for SPA
│       ├── media_bucket/           # Private GCS bucket for travel images
│       ├── firestore/              # Firestore native-mode database
│       ├── seeder_job/             # Cloud Run Job for Firestore seeding
│       ├── load_balancer/          # Global HTTPS LB + CDN + URL map
│       ├── dns/                    # Cloud DNS zone + A record
│       ├── datadog/                # Agentless ddtrace config
│       └── cicd/                   # Cloud Build triggers (backend + frontend + content)
├── docs/
│   └── seeding.md                  # Image upload + Firestore seeding guide
├── scripts/
│   ├── build-and-push.sh           # Manual backend deploy
│   └── deploy-frontend.sh          # Manual frontend deploy
├── tribune_concierge/              # Tribune multi-agent travel team
│   ├── agent.py
│   └── tools/
├── legionnaire_concierge/          # Legionnaire personal assistant
│   ├── agent.py
│   └── tools.py
├── insecure_concierge/             # Debug agent (demo/security testing only)
│   ├── agent.py
│   └── tools.py
├── load-gen/                       # Playwright load generator
│   ├── main.py
│   ├── users.json
│   ├── Dockerfile
│   └── entrypoint.sh
├── docker-compose.yml              # Local dev orchestration
├── .env.example                    # Environment variable template
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
