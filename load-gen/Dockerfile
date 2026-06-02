FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    DD_SERVICE=travel-planner-load-gen \
    DD_ENV=development \
    DD_AGENT_HOST=dd-agent \
    LOAD_GEN_FRONTEND_URL=http://frontend:5173 \
    LOAD_GEN_BACKEND_URL=http://backend:8000 \
    LOAD_GEN_HEADLESS=false \
    DISPLAY=:99

WORKDIR /app/load-gen

COPY load-gen/requirements.txt /tmp/requirements.txt

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        xvfb \
    && pip install --upgrade pip \
    && pip install -r /tmp/requirements.txt \
    && python -m playwright install --with-deps chromium \
    && rm -rf /var/lib/apt/lists/*

COPY load-gen /app/load-gen

CMD ["bash", "/app/load-gen/entrypoint.sh"]
