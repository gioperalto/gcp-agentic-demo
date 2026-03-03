#!/usr/bin/env python3
"""
Test script for Voice WebSocket endpoint.
Connects to /ws/voice, sends a short audio clip, and logs all received events.

Usage:
    1. Start the backend: cd backend && uvicorn main:app --reload
    2. Run this script: python test_voice_ws.py

This sends a 1-second 440Hz sine wave tone as PCM audio, then listens for responses.
"""
import asyncio
import json
import base64
import math
import struct
import sys

WS_URL = "ws://localhost:8000/ws/voice?session_id=test-voice-debug"


def generate_sine_wave_pcm(duration_s=1.0, sample_rate=16000, frequency=440):
    """Generate a sine wave as Int16 LE PCM bytes."""
    num_samples = int(duration_s * sample_rate)
    samples = []
    for i in range(num_samples):
        t = i / sample_rate
        value = int(32767 * 0.3 * math.sin(2 * math.pi * frequency * t))
        samples.append(struct.pack('<h', value))
    return b''.join(samples)


async def test_voice():
    try:
        import websockets
    except ImportError:
        print("Installing websockets...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "websockets"])
        import websockets

    print(f"Connecting to {WS_URL}...")
    async with websockets.connect(WS_URL, ping_interval=None) as ws:
        print("Connected!\n")

        # Generate and send audio
        audio_data = generate_sine_wave_pcm(duration_s=1.5)
        b64_audio = base64.b64encode(audio_data).decode()

        # Send in chunks (like a real mic would)
        chunk_size = 4096  # ~128ms at 16kHz Int16
        b64_chunk_size = (chunk_size * 4) // 3 + 4  # base64 expansion
        print(f"Sending {len(audio_data)} bytes of audio in chunks...")

        for i in range(0, len(audio_data), chunk_size):
            chunk = audio_data[i:i + chunk_size]
            b64_chunk = base64.b64encode(chunk).decode()
            request = {
                "blob": {
                    "data": b64_chunk,
                    "mime_type": "audio/pcm;rate=16000",
                }
            }
            await ws.send(json.dumps(request))
            await asyncio.sleep(0.128)  # ~128ms between chunks

        print("Audio sent. Waiting for response events...\n")

        # Listen for responses with timeout
        event_count = 0
        audio_events = 0
        audio_bytes_total = 0
        transcript_events = 0
        total_transcript = ""

        try:
            while True:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=10.0)
                except asyncio.TimeoutError:
                    print("\n[timeout] No events for 10 seconds, stopping.")
                    break

                event_count += 1
                try:
                    data = json.loads(msg)
                    parts = []

                    # Check for audio
                    if 'content' in data and 'parts' in data.get('content', {}):
                        for part in data['content']['parts']:
                            if 'inlineData' in part:
                                audio_events += 1
                                inline = part['inlineData']
                                b64_data = inline.get('data', '')
                                mime = inline.get('mimeType', 'unknown')
                                # Check for URL-safe base64 characters
                                has_urlsafe = '-' in b64_data or '_' in b64_data
                                raw_bytes = base64.b64decode(b64_data + '==')  # add padding
                                audio_bytes_total += len(raw_bytes)
                                parts.append(
                                    f"AUDIO: {len(raw_bytes)} bytes, "
                                    f"b64_len={len(b64_data)}, "
                                    f"mime={mime}, "
                                    f"url_safe_b64={'YES' if has_urlsafe else 'no'}"
                                )
                            if 'text' in part:
                                parts.append(f"TEXT: \"{part['text'][:80]}\"")

                    # Check for transcription
                    if 'outputTranscription' in data:
                        transcript_events += 1
                        ot = data['outputTranscription']
                        text = ot.get('text', '')
                        total_transcript += text
                        parts.append(f"OUT_TRANSCRIPT: \"{text}\" (finished={ot.get('finished')})")

                    if 'inputTranscription' in data:
                        it = data['inputTranscription']
                        parts.append(f"IN_TRANSCRIPT: \"{it.get('text', '')}\" (finished={it.get('finished')})")

                    if data.get('turnComplete'):
                        parts.append("TURN_COMPLETE")

                    if data.get('partial'):
                        parts.append("partial=true")

                    if 'author' in data:
                        parts.append(f"author={data['author']}")

                    if data.get('interrupted'):
                        parts.append("INTERRUPTED")

                    if not parts:
                        keys = [k for k in data.keys() if data[k] is not None]
                        parts.append(f"other (keys: {keys})")

                    print(f"  Event #{event_count}: {' | '.join(parts)}")

                except json.JSONDecodeError:
                    print(f"  Event #{event_count}: NON-JSON: {msg[:100]}")

        except Exception as e:
            print(f"\n[error] {e}")

        # Summary
        print(f"\n{'='*60}")
        print(f"SUMMARY:")
        print(f"  Total events:     {event_count}")
        print(f"  Audio events:     {audio_events}")
        print(f"  Audio bytes:      {audio_bytes_total} ({audio_bytes_total/24000/2:.1f}s at 24kHz)")
        print(f"  Transcript events: {transcript_events}")
        print(f"  Full transcript:  \"{total_transcript}\"")
        print(f"{'='*60}")

        # Close
        await ws.send(json.dumps({"close": True}))


if __name__ == '__main__':
    asyncio.run(test_voice())
