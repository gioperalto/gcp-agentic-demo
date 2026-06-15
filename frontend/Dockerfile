# Multi-stage build: build SPA with Node, serve with nginx
# In production, dist/ is uploaded to GCS instead of using this image.
# This Dockerfile is useful for local production previews and CI builds.

# --- Build stage ---
FROM node:23.9-alpine AS build
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci
COPY frontend/ ./
ARG VITE_API_BASE_URL=""
ARG VITE_DD_APP_ID=""
ARG VITE_DD_CLIENT_TOKEN=""
ARG VITE_DD_SITE="datadoghq.com"
ARG VITE_DD_SERVICE="travel-planner-frontend"
ARG VITE_DD_VERSION="1.0.0"
ARG VITE_DD_ENV="prod"
RUN npm run build

# --- Serve stage ---
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
