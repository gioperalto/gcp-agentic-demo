# Meridian Frontend

React 18 + TypeScript single-page application built with Vite. Provides the traveler-facing UI for browsing travel options, managing membership cards, and chatting with AI concierge agents.

## Pages

| Route | Page | Description |
|-------|------|-------------|
| `/` | Home | Landing page |
| `/login` | Login | JWT authentication |
| `/flights` | Flights | Browse and purchase flights |
| `/accommodations` | Accommodations | Browse and book hotels, villas, airbnbs |
| `/restaurants` | Restaurants | Browse and reserve restaurants |
| `/experiences` | Experiences | Browse and book local experiences |
| `/concierge` | Concierge | Chat with Legionnaire or Tribune AI concierge |
| `/cards` | Cards | View membership cards |
| `/apply` | Apply | Apply for Legionnaire or Tribune membership |
| `/benefits` | Benefits | Membership benefits and rewards info |
| `/account` | Account | User account and booking history |

## Key Components

- **ChatInput** (`src/components/ChatInput.tsx`): Concierge chat input with voice toggle — microphone is gated to Tribune members only
- **Datadog RUM**: Browser SDK is initialized at app startup for Real User Monitoring (page views, actions, errors)

## Development

```bash
npm install
npm run dev       # Start Vite dev server at http://localhost:5173
npm run build     # Production build
npm run lint      # ESLint
npm run preview   # Preview production build locally
```

## Environment Variables

Set these in a `.env` file at the project root (they are passed in by Docker Compose or Vite's env loading):

| Variable | Description |
|----------|-------------|
| `VITE_API_BASE_URL` | Backend API base URL (default: `http://localhost:8000`) |
| `VITE_DD_APP_ID` | Datadog RUM application ID |
| `VITE_DD_CLIENT_TOKEN` | Datadog RUM client token |
| `VITE_DD_SERVICE` | Datadog RUM service name |
| `VITE_DD_VERSION` | Datadog RUM version tag |
| `VITE_DD_SITE` | Datadog site (e.g. `datadoghq.com`) |
| `VITE_DD_ENV` | Datadog environment tag |

## Tech Stack

- **React 18** — UI library
- **TypeScript** — Type-safe JavaScript
- **React Router** — Client-side routing
- **Vite** — Build tool with HMR
- **Datadog Browser SDK** — Real User Monitoring
