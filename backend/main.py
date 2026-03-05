"""
FastAPI backend for Travel Planner with streaming support
"""
import os, json, asyncio, sys, logging
from dotenv import load_dotenv

# Load env BEFORE any ADK imports so GOOGLE_GENAI_MODEL etc. are available
load_dotenv()

# Text agents need the Vertex AI global endpoint (gemini-3-flash-preview is only
# available there). Voice agents need us-central1, but their Gemini client is
# lazily initialised later — see the /ws/voice handler.
os.environ['GOOGLE_CLOUD_LOCATION'] = 'global'

from ddtrace.llmobs import LLMObs
from ddtrace.appsec.track_user_sdk import track_custom_event
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
from pydantic import BaseModel
from google.adk.runners import InMemoryRunner
from google.adk.agents.live_request_queue import LiveRequest, LiveRequestQueue
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.genai import types

# Add parent directory to path to import tribune_concierge
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tribune_concierge.agent import root_agent, live_root_agent
from legionnaire_concierge.agent import legionnaire_agent


# Datadog LLM Observability setup
LLMObs.enable(
  ml_app=os.getenv("DD_LLMOBS_ML_APP", "travel-planner"),
  api_key=os.getenv("DATADOG_API_KEY"),
  site=os.getenv("DD_SITE", "datadoghq.com"),
  agentless_enabled=True,
  env=os.getenv("DD_ENV", "dev"),
  service=os.getenv("DD_SERVICE", "travel-planner-api"),
)

# Create runner instances
runner = InMemoryRunner(agent=root_agent, app_name="travel-planner")
legionnaire_runner = InMemoryRunner(agent=legionnaire_agent, app_name="legionnaire-concierge")
live_runner = InMemoryRunner(agent=live_root_agent, app_name="tribune-concierge-live")

app = FastAPI(title="Travel Planner API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[
        "x-datadog-trace-id",
        "x-datadog-parent-id",
        "x-datadog-sampling-priority",
        "x-datadog-origin",
        "traceparent",
        "tracestate",
    ],
)

# Include routers
from routers import auth, cards, travel, flights, accommodations

app.include_router(auth.router)
app.include_router(cards.router)
app.include_router(travel.router)
app.include_router(flights.router)
app.include_router(accommodations.router)


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ChatMessage(BaseModel):
    type: str  # "agent_transfer", "content", "done", "error"
    data: dict

def get_agent_friendly_message(agent_name: str) -> str:
    """Generate user-friendly transfer messages based on agent name"""
    messages = {
        "Jenny": "Transferring you to Jenny, our flight specialist. She'll help you find the best flights! ✈️",
        "Marcus": "Connecting you with Marcus, our accommodation expert. He'll help you find the perfect place to stay! 🏨",
        "Sofia": "Bringing in Sofia, our itinerary specialist. She'll help plan your perfect trip! 🗺️",
        "Luca": "Connecting you with Luca, our restaurant specialist. He'll help you find amazing dining experiences! 🍽️",
        "Sam": "Returning to Sam, your travel planner! 🌟"
    }
    return messages.get(agent_name, f"Transferring you to {agent_name}...")


async def stream_legionnaire_response(message: str, session_id: str) -> AsyncGenerator[str, None]:
    """
    Stream legionnaire agent responses (basic concierge without subagents)
    """
    async def run_legionnaire_agent(message: str, session_id: str) -> AsyncGenerator[str, None]:
        """
        Run the legionnaire agent and stream events
        """
        # Run the agent with async streaming
        async for event in legionnaire_runner.run_async(
            user_id=session_id,
            session_id=session_id,
            new_message=types.Content(
                role="user",
                parts=[types.Part(text=message)]
            )
        ):
            # Get the content from the event
            event_content = None
            if hasattr(event, 'content'):
                event_content = event.content

            # Skip echoed user input events to avoid duplicate messages
            if event_content and hasattr(event_content, 'role') and event_content.role == 'user':
                continue

            # Stream content based on event type
            content_text = None

            # Handle Google ADK Event objects with content.parts
            if event_content and hasattr(event_content, 'parts') and event_content.parts:
                text_parts = []
                for part in event_content.parts:
                    if hasattr(part, 'text') and part.text:
                        text_parts.append(part.text)

                if text_parts:
                    content_text = ''.join(text_parts)

            if content_text:
                content_msg = ChatMessage(
                    type="content",
                    data={"text": content_text}
                )
                yield f"data: {content_msg.model_dump_json()}\n\n"
                await asyncio.sleep(0.01)

        # Send completion message
        done_msg = ChatMessage(
            type="done",
            data={"message": "Response complete"}
        )
        yield f"data: {done_msg.model_dump_json()}\n\n"

    try:
        # Ensure session exists before running the agent
        existing_session = await legionnaire_runner.session_service.get_session(
            app_name="legionnaire-concierge",
            user_id=session_id,
            session_id=session_id
        )

        if existing_session is None:
            # Create new session with the frontend-provided session_id
            await legionnaire_runner.session_service.create_session(
                app_name="legionnaire-concierge",
                user_id=session_id,
                session_id=session_id
            )

        # Run the agent and stream responses
        async for event in run_legionnaire_agent(message, session_id):
            yield event

    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"Error in stream_legionnaire_response: {error_detail}")

        error_msg = ChatMessage(
            type="error",
            data={"message": str(e), "detail": error_detail}
        )
        yield f"data: {error_msg.model_dump_json()}\n\n"


async def stream_agent_response(message: str, session_id: str) -> AsyncGenerator[str, None]:
    """
    Stream agent responses with agent transfer notifications
    """
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

            # Skip echoed user input events to avoid duplicate messages
            if event_content and hasattr(event_content, 'role') and event_content.role == 'user':
                continue

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
        sub_agents = {"Jenny", "Marcus", "Sofia", "Luca"}  # Known sub-agents

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


@app.post("/api/chat/legionnaire/stream")
async def legionnaire_chat_stream(request: ChatRequest):
    """
    Stream chat responses for Legionnaire cardholders (basic concierge without subagents)
    """
    return StreamingResponse(
        stream_legionnaire_response(request.message, request.session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream chat responses with Server-Sent Events (Tribune Premium - with subagents)
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


@app.websocket("/ws/voice")
async def voice_websocket(websocket: WebSocket, session_id: str = "default"):
    """
    Real-time bidirectional voice conversation via Gemini Live API.
    Browser sends JSON LiveRequest frames (audio as base64 blob).
    Server streams back JSON Event frames (audio, transcripts, tool calls).
    """
    # Voice model requires the us-central1 regional endpoint.
    # Set this before the live Gemini client is lazily initialised.
    os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'

    await websocket.accept()

    # Ensure session exists
    existing_session = await live_runner.session_service.get_session(
        app_name="tribune-concierge-live",
        user_id=session_id,
        session_id=session_id,
    )
    if existing_session is None:
        existing_session = await live_runner.session_service.create_session(
            app_name="tribune-concierge-live",
            user_id=session_id,
            session_id=session_id,
        )

    live_request_queue = LiveRequestQueue()

    run_config = RunConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Zephyr"),
            ),
        ),
        output_audio_transcription=types.AudioTranscriptionConfig(),
        input_audio_transcription=types.AudioTranscriptionConfig(),
        streaming_mode=StreamingMode.BIDI,
    )

    logger = logging.getLogger("voice_ws")

    last_author = None

    # Transcription accumulators for LLMObs spans
    user_transcript_parts: list[str] = []
    agent_transcript_parts: list[str] = []
    current_agent_name: str = "Sam"

    live_model_name = os.getenv("GOOGLE_GENAI_LIVE_MODEL", "gemini-live-2.5-flash-native-audio")

    def _flush_voice_turn_span(*, interrupted: bool = False) -> None:
        """Create an LLMObs span for the completed voice turn and reset accumulators."""
        nonlocal user_transcript_parts, agent_transcript_parts
        user_text = "".join(user_transcript_parts).strip()
        agent_text = "".join(agent_transcript_parts).strip()
        if not user_text and not agent_text:
            return
        span_name = f"voice_llm.{current_agent_name}"
        if interrupted:
            span_name += ".interrupted"
        with LLMObs.llm(
            model_name=live_model_name,
            model_provider="google",
            name=span_name,
        ) as span:
            LLMObs.annotate(
                span=span,
                input_data=[{"content": user_text or "(audio-only)", "role": "user"}],
                output_data=[{"content": agent_text or "(audio-only)", "role": "assistant"}],
            )
        user_transcript_parts = []
        agent_transcript_parts = []

    async def forward_events():
        """Stream events from runner.run_live() back to the browser."""
        nonlocal last_author, user_transcript_parts, agent_transcript_parts, current_agent_name
        try:
            with LLMObs.workflow(name="voice_session") as _workflow_span:
                async for event in live_runner.run_live(
                    user_id=session_id,
                    session_id=session_id,
                    live_request_queue=live_request_queue,
                    run_config=run_config,
                ):
                    # Serialize once as dict so we can inspect transcription fields
                    event_dict = event.model_dump(exclude_none=True, by_alias=True)

                    # Log agent transfers for debugging
                    author = event_dict.get("author")
                    if author and author != last_author:
                        logger.info("Agent transfer: %s → %s (session %s)", last_author, author, session_id)
                        last_author = author
                        current_agent_name = author

                    # Accumulate output transcription (agent speaking)
                    out_t = event_dict.get("outputTranscription")
                    if out_t and out_t.get("text"):
                        if out_t.get("finished"):
                            agent_transcript_parts = [out_t["text"]]
                        else:
                            agent_transcript_parts.append(out_t["text"])

                    # Accumulate input transcription (user speaking)
                    in_t = event_dict.get("inputTranscription")
                    if in_t and in_t.get("text"):
                        if in_t.get("finished"):
                            user_transcript_parts = [in_t["text"]]
                        else:
                            user_transcript_parts.append(in_t["text"])

                    # Flush span on turn boundaries
                    if event_dict.get("interrupted"):
                        _flush_voice_turn_span(interrupted=True)
                    elif event_dict.get("turnComplete"):
                        _flush_voice_turn_span(interrupted=False)

                    await websocket.send_text(
                        event.model_dump_json(exclude_none=True, by_alias=True)
                    )
        except Exception:
            logger.exception("forward_events error for session %s", session_id)
            raise

    async def keepalive():
        """Send periodic pings so the frontend watchdog stays alive during
        long operations like agent-transfer tool calls."""
        try:
            while True:
                await asyncio.sleep(20)
                if websocket.client_state.name == "CONNECTED":
                    await websocket.send_text('{"ping":true}')
        except Exception:
            pass  # connection closed — let the other tasks handle it

    async def process_messages():
        """Receive JSON LiveRequest frames from browser and feed to queue."""
        try:
            while True:
                data = await websocket.receive_text()
                try:
                    live_request_queue.send(LiveRequest.model_validate_json(data))
                except Exception as e:
                    logger.warning("Invalid LiveRequest frame (session %s): %s", session_id, e)
        except WebSocketDisconnect:
            logger.info("Client disconnected, closing queue for session %s", session_id)
            live_request_queue.close()

    tasks = [
        asyncio.create_task(forward_events()),
        asyncio.create_task(process_messages()),
        asyncio.create_task(keepalive()),
    ]
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
    try:
        for task in done:
            task.result()
    except WebSocketDisconnect:
        logger.info("Voice WebSocket client disconnected: %s", session_id)
    except Exception as e:
        logger.exception("Voice WebSocket error for session %s", session_id)
        try:
            await websocket.close(code=1011, reason=str(e)[:123])
        except Exception:
            pass
    finally:
        live_request_queue.close()
        for task in pending:
            task.cancel()
        await asyncio.gather(*pending, return_exceptions=True)



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
        reload=True,
        reload_dirs=["/app/backend", "/app/tribune_concierge", "/app/legionnaire_concierge"],
    )
