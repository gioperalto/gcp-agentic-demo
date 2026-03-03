FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt
COPY backend/ /app/backend/
COPY tribune_concierge/ /app/tribune_concierge/
COPY legionnaire_concierge/ /app/legionnaire_concierge/
WORKDIR /app/backend
EXPOSE 8000
CMD ["ddtrace-run", "python", "main.py"]
