"""
FastAPI backend for Travel Planner with streaming support
"""
import os, json, asyncio, sys
from ddtrace.llmobs import LLMObs
from ddtrace.llmobs.decorators import workflow, agent
from ddtrace.appsec.track_user_sdk import track_custom_event
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
from pydantic import BaseModel
from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from google.genai import types

# Add parent directory to path to import travel_planner
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from travel_planner.agent import root_agent

# Load environment variables
load_dotenv()

# Datadog LLM Observability setup
LLMObs.enable(
  ml_app="travel-planner",
  api_key=os.getenv("DATADOG_API_KEY"),
  site=os.getenv("DD_SITE", "datadoghq.com"),
  agentless_enabled=True,
  env=os.getenv("ENV", "development"),
  service="travel-planner-api",
)

# Create runner instance
runner = InMemoryRunner(agent=root_agent, app_name="travel-planner")

app = FastAPI(title="Travel Planner API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from routers import auth, cards

app.include_router(auth.router)
app.include_router(cards.router)


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ChatMessage(BaseModel):
    type: str  # "agent_transfer", "content", "done", "error"
    data: dict

@agent
def get_agent_friendly_message(agent_name: str) -> str:
    """Generate user-friendly transfer messages based on agent name"""
    messages = {
        "Jenny": "Transferring you to Jenny, our flight specialist. She'll help you find the best flights! ✈️",
        "Marcus": "Connecting you with Marcus, our accommodation expert. He'll help you find the perfect place to stay! 🏨",
        "Sofia": "Bringing in Sofia, our itinerary specialist. She'll help plan your perfect trip! 🗺️",
        "Luca": "Connecting you with Luca, our restaurant specialist. He'll help you find amazing dining experiences! 🍽️",
        "Alex": "Connecting you with Alex, our budget manager. They'll help you manage your travel costs! 💰",
        "Sam": "Returning to Sam, your travel planner! 🌟"
    }
    return messages.get(agent_name, f"Transferring you to {agent_name}...")


async def stream_agent_response(message: str, session_id: str) -> AsyncGenerator[str, None]:
    """
    Stream agent responses with agent transfer notifications
    """
    @workflow(session_id=session_id)
    async def run_agent(message: str, session_id: str, current_agent: str, sub_agents: set) -> AsyncGenerator[str, None]:
        """
        Run the agent and stream events with agent transfer notifications
        """
        # Run the agent with async streaming
        async for event in runner.run_async(
            user_id=session_id,  # Use session_id as user_id for anonymous users
            session_id=session_id,
            new_message=types.Content(
                role="user",
                parts=[types.Part(text=message)]
            )
        ):
            # Get the content from the event - events have a 'content' attribute with parts
            event_content = None
            if hasattr(event, 'content'):
                event_content = event.content

            # Check for agent transfers by examining event attributes
            event_agent = None

            # Try to get agent name from various possible attributes
            if hasattr(event, 'agent'):
                event_agent = event.agent
            elif hasattr(event, 'agent_name'):
                event_agent = event.agent_name
            elif hasattr(event, 'metadata') and isinstance(event.metadata, dict):
                event_agent = event.metadata.get('agent_name') or event.metadata.get('agent')
            # Check for agent transfer in content parts (Google ADK function calls)
            elif event_content and hasattr(event_content, 'parts') and event_content.parts:
                for part in event_content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        func_call = part.function_call
                        if hasattr(func_call, 'name') and func_call.name == 'transfer_to_agent':
                            if hasattr(func_call, 'args') and isinstance(func_call.args, dict):
                                event_agent = func_call.args.get('agent_name')
                                break

            # Stream content based on event type
            content_text = None

            # Handle Google ADK Event objects with content.parts
            if event_content and hasattr(event_content, 'parts') and event_content.parts:
                # Extract text from parts, ignoring function calls and responses
                text_parts = []
                has_function_call = False
                has_function_response = False

                for part in event_content.parts:
                    if hasattr(part, 'text') and part.text:
                        text_parts.append(part.text)
                    elif hasattr(part, 'function_call'):
                        has_function_call = True
                    elif hasattr(part, 'function_response'):
                        has_function_response = True

                if text_parts:
                    content_text = ''.join(text_parts)

            # Detect when sub-agent returns to Sam
            # If we have content but no explicit agent identifier, and we're currently with a sub-agent,
            # then we've returned to Sam
            # if content_text and not event_agent and current_agent in sub_agents:
            #     event_agent = "Sam"

            # Send transfer message if agent changed
            if event_agent and event_agent != current_agent:
                current_agent = event_agent
                transfer_msg = ChatMessage(
                    type="agent_transfer",
                    data={
                        "agent": event_agent,
                        "message": get_agent_friendly_message(event_agent)
                    }
                )
                yield f"data: {transfer_msg.model_dump_json()}\n\n"
                await asyncio.sleep(0.1)

            if content_text:
                content_msg = ChatMessage(
                    type="content",
                    data={"text": content_text}
                )
                yield f"data: {content_msg.model_dump_json()}\n\n"
                await asyncio.sleep(0.01)  # Small delay to avoid overwhelming client

        # Send completion message
        done_msg = ChatMessage(
            type="done",
            data={"message": "Response complete"}
        )
        yield f"data: {done_msg.model_dump_json()}\n\n"

    try:
        current_agent = "Sam"  # Start with root agent
        sub_agents = {"Jenny", "Marcus", "Sofia", "Luca", "Alex"}  # Known sub-agents

        # Ensure session exists before running the agent
        existing_session = await runner.session_service.get_session(
            app_name="travel-planner",
            user_id=session_id,
            session_id=session_id
        )

        if existing_session is None:
            # Create new session with the frontend-provided session_id
            await runner.session_service.create_session(
                app_name="travel-planner",
                user_id=session_id,
                session_id=session_id
            )

        # Run the agent and stream responses
        async for event in run_agent(message, session_id, current_agent, sub_agents):
            yield event

    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"Error in stream_agent_response: {error_detail}")

        error_msg = ChatMessage(
            type="error",
            data={"message": str(e), "detail": error_detail}
        )
        yield f"data: {error_msg.model_dump_json()}\n\n"


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream chat responses with Server-Sent Events
    """
    return StreamingResponse(
        stream_agent_response(request.message, request.session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "travel-planner"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Travel Planner API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
