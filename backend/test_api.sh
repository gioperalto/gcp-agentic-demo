#!/bin/bash

# Test the streaming API endpoint
echo "Testing the chat stream API..."
echo ""

curl -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I need to find flights from San Francisco to Tokyo",
    "session_id": "test-session-123"
  }' \
  --no-buffer

echo ""
echo "Test complete!"
