"""
Test script to debug agent responses with tool calls
"""
import os
import sys
import asyncio
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from travel_planner.agent import root_agent
from google.adk.runners import InMemoryRunner
from google.genai import types


async def test_agent():
    """Test the agent with a simple query that should trigger a tool call"""
    runner = InMemoryRunner(agent=root_agent, app_name="travel-planner-test")

    session_id = "test-session-001"

    # Create session
    await runner.session_service.create_session(
        app_name="travel-planner-test",
        user_id=session_id,
        session_id=session_id
    )

    print("=" * 80)
    print("Testing agent with a query that should trigger Jenny (flight agent)")
    print("=" * 80)

    message = "I need to find flights from New York to London for next week"

    print(f"\nUser message: {message}\n")
    print("Events received:")
    print("-" * 80)

    event_count = 0
    async for event in runner.run_async(
        user_id=session_id,
        session_id=session_id,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text=message)]
        )
    ):
        event_count += 1
        print(f"\n[Event {event_count}]")
        print(f"Type: {type(event).__name__}")
        print(f"All attributes: {dir(event)}")

        # Check for specific attributes
        if hasattr(event, 'content'):
            print(f"Has content: {event.content}")
        if hasattr(event, 'message'):
            print(f"Has message: {event.message}")
        if hasattr(event, 'data'):
            print(f"Has data: {event.data}")

        if hasattr(event, 'role'):
            print(f"Role: {event.role}")

        if hasattr(event, 'parts') and event.parts:
            print(f"Number of parts: {len(event.parts)}")
            for i, part in enumerate(event.parts):
                part_type = type(part).__name__
                print(f"  Part {i+1}: {part_type}")

                if hasattr(part, 'text') and part.text:
                    text_preview = part.text[:100] + "..." if len(part.text) > 100 else part.text
                    print(f"    Text: {text_preview}")

                if hasattr(part, 'function_call') and part.function_call:
                    fc = part.function_call
                    print(f"    Function Call: {fc.name if hasattr(fc, 'name') else 'unknown'}")
                    if hasattr(fc, 'args'):
                        print(f"    Args: {fc.args}")

                if hasattr(part, 'function_response') and part.function_response:
                    fr = part.function_response
                    print(f"    Function Response: {fr.name if hasattr(fr, 'name') else 'unknown'}")
                    if hasattr(fr, 'response'):
                        response_preview = str(fr.response)[:100] + "..." if len(str(fr.response)) > 100 else str(fr.response)
                        print(f"    Response: {response_preview}")

        # Try to access the text property to see if it triggers the warning
        if hasattr(event, 'text'):
            try:
                text = event.text
                if text:
                    print(f"Event.text: {text[:100] + '...' if len(text) > 100 else text}")
                else:
                    print(f"Event.text: (empty)")
            except Exception as e:
                print(f"Error accessing event.text: {e}")

    print("\n" + "=" * 80)
    print(f"Total events received: {event_count}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_agent())
