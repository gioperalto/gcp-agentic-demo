"""
FastAPI backend for Travel Planner with streaming support
"""
import os, json, asyncio, sys, logging, logging.config, time
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load env BEFORE any ADK imports so GOOGLE_GENAI_MODEL etc. are available
load_dotenv()

# Default to global endpoint at startup. Text agents reset to 'global' before
# each request since the voice handler temporarily switches to 'us-central1'.
os.environ['GOOGLE_CLOUD_LOCATION'] = 'global'

from ddtrace.llmobs import LLMObs
from ddtrace.trace import tracer

# Hallucination detection (LLM-as-judge) — runs async after each concierge turn.
# The experiments package lives outside the backend Docker image, so import is
# optional: when unavailable the judge is silently skipped.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
try:
    from experiments.hallucination_evaluator import hallucination_judge
except ImportError:
    hallucination_judge = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# JSON log formatter with Datadog trace correlation
# ---------------------------------------------------------------------------
# ddtrace-run (with DD_LOGS_INJECTION=true) patches every LogRecord to carry
# dd.trace_id, dd.span_id, dd.service, dd.env, and dd.version.  Outputting
# them as top-level JSON fields lets the Datadog agent parse and correlate
# logs with APM traces automatically — no custom log pipeline needed.
#
# We also override uvicorn's loggers so its access/error lines go through the
# same JSON formatter (uvicorn normally uses its own plain-text formatters).
# ---------------------------------------------------------------------------

_DD_LOG_ATTRS = ("dd.trace_id", "dd.span_id", "dd.service", "dd.env", "dd.version")


class _JSONFormatter(logging.Formatter):
    """Minimal JSON formatter that includes ddtrace correlation fields."""

    def format(self, record: logging.LogRecord) -> str:
        msg = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "filename": record.filename,
            "lineno": record.lineno,
        }
        # Append ddtrace correlation attributes (injected by ddtrace-run)
        for attr in _DD_LOG_ATTRS:
            val = getattr(record, attr, "")
            if val:
                msg[attr] = str(val)
        # Include exception info if present
        if record.exc_info and record.exc_info[0] is not None:
            msg["error"] = self.formatException(record.exc_info)
        return json.dumps(msg, default=str)


LOGGING_CONFIG: dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {"()": _JSONFormatter},
    },
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "stream": "ext://sys.stdout",
        },
    },
    "root": {
        "handlers": ["stdout"],
        "level": "INFO",
    },
    "loggers": {
        # Override uvicorn loggers so they also emit JSON with DD fields
        "uvicorn": {"handlers": ["stdout"], "level": "INFO", "propagate": False},
        "uvicorn.error": {"handlers": ["stdout"], "level": "INFO", "propagate": False},
        "uvicorn.access": {"handlers": ["stdout"], "level": "INFO", "propagate": False},
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
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

from tribune_concierge.agent import root_agent, live_root_agent, AGENT_VOICE_MAP, LIVE_AGENT_MAP
from legionnaire_concierge.agent import legionnaire_agent
from insecure_concierge.agent import insecure_agent
from services.feature_flag_service import evaluate_flag, init_feature_flags

logger = logging.getLogger("travel_planner")

# Datadog LLM Observability is initialised by ddtrace-run (see Dockerfile CMD).
# Do NOT call LLMObs.enable() here — combining it with ddtrace-run is unsupported
# and causes spans to be silently dropped.  Configuration lives in env vars:
#   DD_LLMOBS_ENABLED=1, DD_LLMOBS_ML_APP, DD_LLMOBS_AGENTLESS_ENABLED, etc.
# Manual spans (LLMObs.llm(), LLMObs.workflow()) still work without enable().

# Create runner instances
runner = InMemoryRunner(agent=root_agent, app_name="travel-planner")
legionnaire_runner = InMemoryRunner(agent=legionnaire_agent, app_name="legionnaire-concierge")
insecure_runner = InMemoryRunner(agent=insecure_agent, app_name="insecure-concierge")
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

# Initialize Datadog Feature Flags (OpenFeature SDK)
init_feature_flags()

# Include routers
from routers import auth, cards, travel, flights, accommodations, feature_flags

app.include_router(auth.router)
app.include_router(cards.router)
app.include_router(travel.router)
app.include_router(flights.router)
app.include_router(accommodations.router)
app.include_router(feature_flags.router)


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


async def traced_sse_stream(
    generator: AsyncGenerator[str, None],
    *,
    resource: str,
    session_id: str,
    http_request: Request | None = None,
) -> AsyncGenerator[str, None]:
    """Wrap an SSE generator with an explicit ddtrace span.

    ddtrace's auto-instrumentation finishes the HTTP request span when the
    endpoint function returns, but for ``StreamingResponse`` the actual work
    happens *after* that — inside the async generator.  This helper creates a
    child span that stays open for the full duration of the stream and
    guarantees it closes in a ``finally`` block so the trace is never dropped.
    """
    from ddtrace.contrib.asgi import span_from_scope

    # In ddtrace v4 tracer.trace() auto-parents to the active span.
    # The SSE generator runs after the request handler returns, so the
    # request span may no longer be active.  Re-activate it so the
    # stream span becomes a proper child of the HTTP request trace.
    parent_span = None
    if http_request is not None:
        parent_span = span_from_scope(http_request.scope)
    if parent_span is not None:
        tracer.context_provider.activate(parent_span)

    with tracer.trace(
        "chat.sse.stream",
        resource=resource,
    ) as span:
        span.set_tag("sse.endpoint", resource)
        span.set_tag("session.id", session_id)
        try:
            async for chunk in generator:
                yield chunk
        except asyncio.CancelledError:
            span.set_tag("stream.cancelled", True)
            raise
        except Exception:
            span.set_exc_info(*sys.exc_info())
            raise
        finally:
            span.set_tag("stream.finished", True)


_genai_model = os.getenv("GOOGLE_GENAI_MODEL", "gemini-2.0-flash")


async def stream_legionnaire_response(message: str, session_id: str) -> AsyncGenerator[str, None]:
    """
    Stream legionnaire agent responses (basic concierge without subagents)
    """
    # Ensure text requests always use the global endpoint (voice may have switched to us-central1)
    os.environ['GOOGLE_CLOUD_LOCATION'] = 'global'

    response_parts: list[str] = []
    tool_context: list[str] = []       # ground truth from tool calls

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
                    # Capture tool results as ground truth for hallucination detection
                    elif hasattr(part, 'function_response') and part.function_response:
                        try:
                            fr = part.function_response
                            resp_data = fr.response if hasattr(fr, 'response') else str(fr)
                            if isinstance(resp_data, dict):
                                tool_context.append(json.dumps(resp_data, default=str))
                            else:
                                tool_context.append(str(resp_data))
                        except Exception:
                            pass

                if text_parts:
                    content_text = ''.join(text_parts)

            if content_text:
                response_parts.append(content_text)
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

        with LLMObs.workflow(name="legionnaire_concierge") as workflow_span:
            LLMObs.annotate(span=workflow_span, tags={"session.id": session_id})

            # Run the agent and stream responses
            async for event in run_legionnaire_agent(message, session_id):
                yield event

            # Flush an agent span with the full input/output for this turn
            with LLMObs.agent(
                name="text_agent.legionnaire",
            ) as llm_span:
                LLMObs.annotate(
                    span=llm_span,
                    input_data=[{"content": message, "role": "user"}],
                    output_data=[{"content": "".join(response_parts), "role": "assistant"}],
                    metadata={"model": _genai_model, "model_provider": "google"},
                )

            # Run hallucination detection asynchronously (non-blocking)
            if hallucination_judge is not None:
                full_response = "".join(response_parts)
                asyncio.create_task(
                    hallucination_judge(
                        user_message=message,
                        agent_response=full_response,
                        tool_context=tool_context,
                        workflow_span=workflow_span,
                        agent_name="legionnaire",
                    )
                )

    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        logger.exception("Error in stream_legionnaire_response")

        error_msg = ChatMessage(
            type="error",
            data={"message": str(e), "detail": error_detail}
        )
        yield f"data: {error_msg.model_dump_json()}\n\n"


async def stream_insecure_response(message: str, session_id: str) -> AsyncGenerator[str, None]:
    """
    Stream insecure debug agent responses (unrestricted user data access)
    """
    # Ensure text requests always use the global endpoint (voice may have switched to us-central1)
    os.environ['GOOGLE_CLOUD_LOCATION'] = 'global'

    response_parts: list[str] = []

    async def run_insecure_agent(message: str, session_id: str) -> AsyncGenerator[str, None]:
        """
        Run the insecure agent and stream events
        """
        # Run the agent with async streaming
        async for event in insecure_runner.run_async(
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
                response_parts.append(content_text)
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
        existing_session = await insecure_runner.session_service.get_session(
            app_name="insecure-concierge",
            user_id=session_id,
            session_id=session_id
        )

        if existing_session is None:
            # Create new session with the frontend-provided session_id
            await insecure_runner.session_service.create_session(
                app_name="insecure-concierge",
                user_id=session_id,
                session_id=session_id
            )

        with LLMObs.workflow(name="insecure_concierge") as workflow_span:
            LLMObs.annotate(span=workflow_span, tags={"session.id": session_id})

            # Run the agent and stream responses
            async for event in run_insecure_agent(message, session_id):
                yield event

            # Flush an agent span with the full input/output for this turn
            with LLMObs.agent(
                name="text_agent.insecure",
            ) as llm_span:
                LLMObs.annotate(
                    span=llm_span,
                    input_data=[{"content": message, "role": "user"}],
                    output_data=[{"content": "".join(response_parts), "role": "assistant"}],
                    metadata={"model": _genai_model, "model_provider": "google"},
                )

    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        logger.exception("Error in stream_insecure_response")

        error_msg = ChatMessage(
            type="error",
            data={"message": str(e), "detail": error_detail}
        )
        yield f"data: {error_msg.model_dump_json()}\n\n"


async def stream_agent_response(message: str, session_id: str) -> AsyncGenerator[str, None]:
    """
    Stream agent responses with agent transfer notifications
    """
    # Ensure text requests always use the global endpoint (voice may have switched to us-central1)
    os.environ['GOOGLE_CLOUD_LOCATION'] = 'global'

    # Per-agent response accumulators for LLMObs spans
    agent_response_parts: list[str] = []
    all_response_parts: list[str] = []    # full turn accumulator for hallucination judge
    tool_context: list[str] = []          # ground truth from tool calls
    current_agent = "Sam"

    def _flush_text_turn_span(agent_name: str) -> None:
        """Create an LLMObs agent span for the text accumulated by the current agent."""
        nonlocal agent_response_parts
        agent_text = "".join(agent_response_parts).strip()
        if not agent_text:
            return
        with LLMObs.agent(
            name=f"text_agent.{agent_name}",
        ) as span:
            LLMObs.annotate(
                span=span,
                input_data=[{"content": message, "role": "user"}],
                output_data=[{"content": agent_text, "role": "assistant"}],
                metadata={"model": _genai_model, "model_provider": "google"},
            )
        agent_response_parts = []

    async def run_agent(message: str, session_id: str, sub_agents: set) -> AsyncGenerator[str, None]:
        """
        Run the agent and stream events with agent transfer notifications
        """
        nonlocal current_agent, agent_response_parts

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
                    elif hasattr(part, 'function_response') and part.function_response:
                        has_function_response = True
                        # Capture tool results as ground truth for hallucination detection
                        try:
                            fr = part.function_response
                            resp_data = fr.response if hasattr(fr, 'response') else str(fr)
                            if isinstance(resp_data, dict):
                                tool_context.append(json.dumps(resp_data, default=str))
                            else:
                                tool_context.append(str(resp_data))
                        except Exception:
                            pass

                if text_parts:
                    content_text = ''.join(text_parts)

            # Detect when sub-agent returns to Sam
            # If we have content but no explicit agent identifier, and we're currently with a sub-agent,
            # then we've returned to Sam
            # if content_text and not event_agent and current_agent in sub_agents:
            #     event_agent = "Sam"

            # Send transfer message if agent changed
            if event_agent and event_agent != current_agent:
                # Flush LLMObs span for the outgoing agent before switching
                _flush_text_turn_span(current_agent)
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
                agent_response_parts.append(content_text)
                all_response_parts.append(content_text)
                content_msg = ChatMessage(
                    type="content",
                    data={"text": content_text}
                )
                yield f"data: {content_msg.model_dump_json()}\n\n"
                await asyncio.sleep(0.01)  # Small delay to avoid overwhelming client

        # Flush the final agent's LLM span
        _flush_text_turn_span(current_agent)

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

        with LLMObs.workflow(name="tribune_concierge") as workflow_span:
            LLMObs.annotate(span=workflow_span, tags={"session.id": session_id})

            # Run the agent and stream responses
            async for event in run_agent(message, session_id, sub_agents):
                yield event

            # Run hallucination detection asynchronously (non-blocking)
            if hallucination_judge is not None:
                full_response = "".join(all_response_parts)
                asyncio.create_task(
                    hallucination_judge(
                        user_message=message,
                        agent_response=full_response,
                        tool_context=tool_context,
                        workflow_span=workflow_span,
                        agent_name=f"tribune.{current_agent}",
                    )
                )

    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        logger.exception("Error in stream_agent_response")

        error_msg = ChatMessage(
            type="error",
            data={"message": str(e), "detail": error_detail}
        )
        yield f"data: {error_msg.model_dump_json()}\n\n"


@app.post("/api/chat/legionnaire/stream")
async def legionnaire_chat_stream(http_request: Request, request: ChatRequest):
    """
    Stream chat responses for Legionnaire cardholders (basic concierge without subagents)
    """
    return StreamingResponse(
        traced_sse_stream(
            stream_legionnaire_response(request.message, request.session_id),
            resource="POST /api/chat/legionnaire/stream",
            session_id=request.session_id,
            http_request=http_request,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.post("/api/chat/insecure/stream")
async def insecure_chat_stream(http_request: Request, request: ChatRequest):
    """
    Stream chat responses for the insecure debug agent (gated by feature flag)
    """
    flag_enabled = evaluate_flag("insecure_profile_agent", default=False)
    if not flag_enabled:
        raise HTTPException(status_code=403, detail="Feature not available")
    return StreamingResponse(
        traced_sse_stream(
            stream_insecure_response(request.message, request.session_id),
            resource="POST /api/chat/insecure/stream",
            session_id=request.session_id,
            http_request=http_request,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.post("/api/chat/stream")
async def chat_stream(http_request: Request, request: ChatRequest):
    """
    Stream chat responses with Server-Sent Events (Tribune Premium - with subagents)
    """
    return StreamingResponse(
        traced_sse_stream(
            stream_agent_response(request.message, request.session_id),
            resource="POST /api/chat/stream",
            session_id=request.session_id,
            http_request=http_request,
        ),
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


def _make_voice_run_config(agent_name: str) -> RunConfig:
    """Build a RunConfig with the correct voice for the given agent."""
    voice_info = AGENT_VOICE_MAP.get(agent_name, AGENT_VOICE_MAP["Sam"])
    return RunConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice_info["voice"]),
            ),
        ),
        proactivity=types.ProactivityConfig(proactive_audio=True),
        output_audio_transcription=types.AudioTranscriptionConfig(),
        input_audio_transcription=types.AudioTranscriptionConfig(),
        streaming_mode=StreamingMode.BIDI,
    )


@app.websocket("/ws/voice")
async def voice_websocket(websocket: WebSocket, session_id: str = "default"):
    """
    Real-time bidirectional voice conversation via Gemini Live API.
    Browser sends JSON LiveRequest frames (audio as base64 blob).
    Server streams back JSON Event frames (audio, transcripts, tool calls).

    Supports per-agent voice switching: when an agent calls transfer_to(),
    the current run_live() connection is closed and a new one is opened with
    the target agent's voice configuration.
    """
    # Voice model requires the us-central1 regional endpoint.
    os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'

    await websocket.accept()

    voice_logger = logging.getLogger("voice_ws")
    voice_runner = InMemoryRunner(agent=live_root_agent, app_name="tribune-concierge-live")

    last_author = None
    current_agent_name: str = "Sam"
    current_live_session_id: str = f"{session_id}:0:{current_agent_name}"
    transfer_count = 0

    # Transcription accumulators for LLMObs spans
    user_transcript_parts: list[str] = []
    agent_transcript_parts: list[str] = []
    conversation_history: list[dict[str, str]] = []
    # Deferred-flush flag: set on turnComplete, cleared at the top of the next
    # event iteration after absorbing any trailing transcription frames that
    # arrive after the turnComplete signal (inputTranscription.finished often
    # lags behind the agent's turnComplete in the Live API event stream).
    pending_turn_complete: bool = False

    live_model_name = os.getenv("GOOGLE_GENAI_LIVE_MODEL", "gemini-live-2.5-flash-native-audio")

    # Shared flag for the message receiver task
    client_disconnected = False

    # Captured by the workflow context manager and reactivated inside
    # asyncio tasks so that child spans nest under the workflow trace.
    _workflow_span_ref = None

    def _flush_voice_turn_span(*, interrupted: bool = False) -> None:
        """Create an LLMObs span for the completed voice turn and reset accumulators."""
        nonlocal user_transcript_parts, agent_transcript_parts, conversation_history
        user_text = "".join(user_transcript_parts).strip()
        agent_text = "".join(agent_transcript_parts).strip()
        if not user_text and not agent_text:
            return
        span_name = f"voice_llm.{current_agent_name}"
        if interrupted:
            span_name += ".interrupted"

        # Reactivate the workflow span so this LLM span becomes its child.
        if _workflow_span_ref is not None:
            tracer.context_provider.activate(_workflow_span_ref)

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
        if user_text:
            conversation_history.append({
                "role": "user",
                "agent_name": current_agent_name,
                "text": user_text,
            })
        if agent_text:
            conversation_history.append({
                "role": "agent",
                "agent_name": current_agent_name,
                "text": agent_text,
            })
        user_transcript_parts = []
        agent_transcript_parts = []

    async def forward_events(live_request_queue: LiveRequestQueue, run_config: RunConfig) -> str | None:
        """Stream events from runner.run_live() back to the browser.

        Returns the name of the agent to transfer to, or None if the
        conversation ended normally / client disconnected.
        """
        nonlocal last_author, user_transcript_parts, agent_transcript_parts, pending_turn_complete, current_agent_name, transfer_audio_muted, transfer_audio_muted_since, current_live_session_id

        # Reactivate the workflow span in this async task so all child
        # spans (created by _flush_voice_turn_span) nest under it.
        if _workflow_span_ref is not None:
            tracer.context_provider.activate(_workflow_span_ref)

        pending_transfer_target: str | None = None
        conversation_ended = False
        # If audio was muted (transfer in progress), re-enable after
        # the first turnComplete so the user can speak to the new agent.
        reenable_audio_on_turn = transfer_audio_muted

        try:
            async for event in voice_runner.run_live(
                user_id=session_id,
                session_id=current_live_session_id,
                live_request_queue=live_request_queue,
                run_config=run_config,
            ):
                event_dict = event.model_dump(exclude_none=True, by_alias=True)

                # Log agent author changes
                author = event_dict.get("author")
                if author and author != last_author:
                    voice_logger.info("Agent author: %s → %s (session %s)", last_author, author, session_id)
                    last_author = author
                    current_agent_name = author

                # Detect transfer_to / end_conversation function calls
                content_parts = event_dict.get("content", {}).get("parts", [])
                for part in content_parts:
                    fc = part.get("functionCall")
                    if fc:
                        if fc.get("name") == "transfer_to":
                            pending_transfer_target = fc.get("args", {}).get("agent_name")
                            voice_logger.info("Transfer requested: %s → %s (session %s)",
                                              current_agent_name, pending_transfer_target, session_id)
                        elif fc.get("name") == "end_conversation":
                            conversation_ended = True
                            voice_logger.info("Conversation ended by agent (session %s)", session_id)

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

                # Flush the span deferred from the previous turnComplete now
                # that this event's transcription frames have been absorbed above.
                # This ensures inputTranscription/outputTranscription events that
                # trail the turnComplete signal in the Live API stream are captured
                # before the LLMObs span is written.
                if pending_turn_complete:
                    _flush_voice_turn_span(interrupted=False)
                    pending_turn_complete = False

                # Flush span on turn boundaries
                if event_dict.get("interrupted"):
                    _flush_voice_turn_span(interrupted=True)
                    # Clear stale transfer intent on interruption so it doesn't
                    # fire later when the user was mid-sentence
                    pending_transfer_target = None
                elif event_dict.get("turnComplete"):
                    # Defer the span flush by one event frame so any trailing
                    # transcription events (e.g. inputTranscription.finished) are
                    # captured before the span is written (see pending_turn_complete
                    # check above, which fires at the top of the next iteration).
                    pending_turn_complete = True

                    # Re-enable incoming audio after the new agent's priming
                    # response completes (first turnComplete post-transfer).
                    if reenable_audio_on_turn:
                        _clear_transfer_audio_mute("turn_complete")
                        reenable_audio_on_turn = False
                        voice_logger.info("Audio re-enabled after new agent greeting turn (session %s)", session_id)

                    # After turn completes, act on pending transfer or end.
                    # Flush inline here since we're about to return and won't
                    # process any further events for this turn.
                    if pending_transfer_target:
                        pending_turn_complete = False
                        _flush_voice_turn_span(interrupted=False)
                        # Mute incoming audio until the new agent's first
                        # turnComplete — event-based, not time-based.
                        transfer_audio_muted = True
                        transfer_audio_muted_since = time.monotonic()
                        await websocket.send_text(
                            event.model_dump_json(exclude_none=True, by_alias=True)
                        )
                        await websocket.send_text(json.dumps({
                            "agentTransfer": {
                                "from": current_agent_name,
                                "to": pending_transfer_target,
                                "message": f"Transferring you to {pending_transfer_target}..."
                            }
                        }))
                        return pending_transfer_target

                    if conversation_ended:
                        pending_turn_complete = False
                        _flush_voice_turn_span(interrupted=False)
                        await websocket.send_text(
                            event.model_dump_json(exclude_none=True, by_alias=True)
                        )
                        await websocket.send_text(json.dumps({"conversationEnded": True}))
                        return None

                # Forward event to browser
                await websocket.send_text(
                    event.model_dump_json(exclude_none=True, by_alias=True)
                )

        except Exception:
            voice_logger.exception("forward_events error for session %s", session_id)
            raise

        # Flush any turn that completed right as run_live ended.
        if pending_turn_complete:
            _flush_voice_turn_span(interrupted=False)
            pending_turn_complete = False

        return None  # run_live ended (queue closed / client disconnected)

    async def keepalive():
        """Send periodic pings so the frontend watchdog stays alive."""
        try:
            while True:
                await asyncio.sleep(20)
                if websocket.client_state.name == "CONNECTED":
                    await websocket.send_text('{"ping":true}')
        except Exception:
            pass

    # When True, incoming audio frames are silently dropped (used during transfers
    # to discard in-flight mic data and prevent echo of the new agent's greeting).
    # Normally cleared on the new agent's first turnComplete, with a timeout
    # fallback so a stalled transfer cannot block user speech indefinitely.
    transfer_audio_muted = False
    transfer_audio_muted_since: float | None = None

    def _clear_transfer_audio_mute(reason: str) -> None:
        nonlocal transfer_audio_muted, transfer_audio_muted_since
        if transfer_audio_muted:
            voice_logger.info("Clearing transfer audio mute (%s) for session %s", reason, session_id)
        transfer_audio_muted = False
        transfer_audio_muted_since = None

    async def process_messages(live_request_queue: LiveRequestQueue):
        """Receive JSON LiveRequest frames from browser and feed to queue."""
        nonlocal client_disconnected
        try:
            while True:
                data = await websocket.receive_text()
                try:
                    # During transfers, drop audio-only frames to prevent residual
                    # mic data from triggering a second greeting on the new agent.
                    parsed = json.loads(data)
                    if transfer_audio_muted and "blob" in parsed:
                        if transfer_audio_muted_since is not None and time.monotonic() - transfer_audio_muted_since > 15:
                            _clear_transfer_audio_mute("timeout")
                        else:
                            continue
                    live_request_queue.send(LiveRequest.model_validate_json(data))
                except Exception as e:
                    voice_logger.warning("Invalid LiveRequest frame (session %s): %s", session_id, e)
        except WebSocketDisconnect:
            voice_logger.info("Client disconnected, closing queue for session %s", session_id)
            client_disconnected = True
            live_request_queue.close()

    # Outer loop: each iteration runs one agent until transfer or end
    keepalive_task = asyncio.create_task(keepalive())

    try:
        with LLMObs.workflow(name="voice_session") as _workflow_span:
            _workflow_span_ref = _workflow_span
            LLMObs.annotate(span=_workflow_span, tags={"session.id": session_id})
            priming_message: str | None = None

            while not client_disconnected:
                # Use a fresh ADK live session for each agent stint so transfer
                # tool calls cannot leak into the next agent's history.
                voice_runner.agent = LIVE_AGENT_MAP[current_agent_name]
                existing_session = await voice_runner.session_service.get_session(
                    app_name="tribune-concierge-live",
                    user_id=session_id,
                    session_id=current_live_session_id,
                )
                if existing_session is None:
                    await voice_runner.session_service.create_session(
                        app_name="tribune-concierge-live",
                        user_id=session_id,
                        session_id=current_live_session_id,
                    )
                run_config = _make_voice_run_config(current_agent_name)
                live_request_queue = LiveRequestQueue()

                # Send priming message for transferred agents
                if priming_message:
                    live_request_queue.send(LiveRequest(content=types.Content(
                        role="user",
                        parts=[types.Part(text=priming_message)],
                    )))
                    priming_message = None

                msg_task = asyncio.create_task(process_messages(live_request_queue))
                fwd_task = asyncio.create_task(forward_events(live_request_queue, run_config))

                tasks = [fwd_task, msg_task]
                done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

                # Get the transfer target (if any) from forward_events
                transfer_target: str | None = None
                for task in done:
                    try:
                        result = task.result()
                        if task is fwd_task and isinstance(result, str):
                            transfer_target = result
                    except WebSocketDisconnect:
                        client_disconnected = True
                    except Exception as e:
                        voice_logger.exception("Voice task error for session %s", session_id)
                        client_disconnected = True

                # Clean up pending tasks from this iteration
                live_request_queue.close()
                for task in pending:
                    task.cancel()
                await asyncio.gather(*pending, return_exceptions=True)

                if transfer_target and not client_disconnected:
                    old_agent = current_agent_name
                    current_agent_name = transfer_target
                    transfer_count += 1
                    current_live_session_id = f"{session_id}:{transfer_count}:{current_agent_name}"
                    history_lines = []
                    for entry in conversation_history:
                        speaker = entry["agent_name"] if entry["role"] == "agent" else "Customer"
                        compact_text = " ".join(entry["text"].split())
                        history_lines.append(f'  {speaker}: {json.dumps(compact_text)}')
                    history_block = "\n".join(history_lines) if history_lines else '  Customer: "(no prior conversation captured)"'
                    priming_message = (
                        f"The customer was just transferred to you from {old_agent}.\n"
                        f"Here is a summary of the conversation so far:\n"
                        f"{history_block}\n"
                        f"Reply with exactly one brief greeting sentence acknowledging the context, then wait silently for the user."
                    )
                    voice_logger.info("Agent switch: %s → %s (session %s)", old_agent, current_agent_name, session_id)
                    continue
                else:
                    break  # conversation ended or client disconnected

    except WebSocketDisconnect:
        voice_logger.info("Voice WebSocket client disconnected: %s", session_id)
    except Exception as e:
        voice_logger.exception("Voice WebSocket error for session %s", session_id)
        try:
            await websocket.close(code=1011, reason=str(e)[:123])
        except Exception:
            pass
    finally:
        keepalive_task.cancel()
        await asyncio.gather(keepalive_task, return_exceptions=True)



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
        reload_dirs=["/app/backend", "/app/tribune_concierge", "/app/legionnaire_concierge", "/app/insecure_concierge"],
        log_config=None,  # preserve our JSON formatter with DD trace correlation
    )
