import { useState, useRef, useCallback } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function getWsUrl(): string {
  const base = API_BASE_URL.replace(/^http/, 'ws');
  return base;
}

/** Encode an ArrayBuffer to standard base64 (for sending mic audio) */
function arrayBufferToBase64(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer);
  let binary = '';
  for (let i = 0; i < bytes.length; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

/**
 * Decode base64 (standard or URL-safe) to Uint8Array.
 * The Gemini Live API / Pydantic may emit URL-safe base64 with - and _ chars.
 * JavaScript's atob() only handles standard base64 (+, /, =).
 */
function base64ToUint8Array(b64: string): Uint8Array {
  // Convert URL-safe base64 to standard base64
  let std = b64.replace(/-/g, '+').replace(/_/g, '/');
  // Add padding if needed
  while (std.length % 4 !== 0) std += '=';
  const binary = atob(std);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes;
}

interface VoiceModeState {
  isActive: boolean;
  isConnecting: boolean;
  isSpeaking: boolean;
  currentTranscript: string;
}

interface VoiceModeCallbacks {
  onAgentTranscript?: (text: string, isFinal: boolean) => void;
  onUserTranscript?: (text: string, isFinal: boolean) => void;
  onAgentTransfer?: (agentName: string) => void;
  onToolResult?: (agentName: string, message: string, toolName?: string) => void;
  onConversationEnd?: () => void;
  onError?: (error: string) => void;
}

export function useVoiceMode(sessionId: string, callbacks?: VoiceModeCallbacks) {
  const [state, setState] = useState<VoiceModeState>({
    isActive: false,
    isConnecting: false,
    isSpeaking: false,
    currentTranscript: '',
  });

  const wsRef = useRef<WebSocket | null>(null);
  const captureCtxRef = useRef<AudioContext | null>(null);
  const micStreamRef = useRef<MediaStream | null>(null);
  const micMutedRef = useRef(false);
  const isActiveRef = useRef(false);

  // Playback: use AudioContext + BufferSource scheduling (matching ADK reference)
  const playbackCtxRef = useRef<AudioContext | null>(null);
  const nextPlayTimeRef = useRef<number>(0);

  // Idle watchdog: detect stale connections (e.g. server hung during agent transfer)
  const lastEventTimeRef = useRef<number>(0);
  const watchdogIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Transcript accumulation
  const agentTranscriptRef = useRef<string>('');
  const userTranscriptRef = useRef<string>('');
  const callbacksRef = useRef(callbacks);
  callbacksRef.current = callbacks;

  // Track whether to suppress the first agent transcript (initial greeting)
  const suppressGreetingRef = useRef(false);
  // Track whether a transfer TTS is playing (prevents turnComplete from unmuting mic)
  const transferTTSPlayingRef = useRef(false);
  // Track whether we're waiting for the NEW agent's first turnComplete after transfer
  const awaitingTransferTurnRef = useRef(false);
  // Track the current speaking agent to detect actual transfers (not per-event noise)
  const currentAuthorRef = useRef<string>('Sam');
  const transferFallbackTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  /**
   * Schedule Int16 LE PCM audio for immediate gapless playback.
   * Mirrors the ADK reference implementation's AudioPlayingService.
   */
  function playPCM(pcmBytes: Uint8Array) {
    const ctx = playbackCtxRef.current;
    if (!ctx || ctx.state === 'closed') return;
    if (ctx.state === 'suspended') ctx.resume();

    const sampleCount = Math.floor(pcmBytes.length / 2);
    if (sampleCount === 0) return;

    // Decode Int16 little-endian → Float32 (matching ADK's manual byte decoding)
    const float32 = new Float32Array(sampleCount);
    for (let i = 0; i < sampleCount; i++) {
      let sample = pcmBytes[i * 2] | (pcmBytes[i * 2 + 1] << 8);
      if (sample >= 32768) sample -= 65536; // unsigned → signed
      float32[i] = sample / 32768;
    }

    // Create AudioBuffer and schedule playback
    const buffer = ctx.createBuffer(1, float32.length, ctx.sampleRate);
    buffer.copyToChannel(float32, 0);
    const source = ctx.createBufferSource();
    source.buffer = buffer;
    source.connect(ctx.destination);

    // Schedule seamlessly after previous chunk (no gaps, no overlaps)
    const now = ctx.currentTime;
    const startTime = Math.max(nextPlayTimeRef.current, now);
    source.start(startTime);
    nextPlayTimeRef.current = startTime + buffer.duration;
  }

  const cleanup = useCallback(() => {
    if (transferFallbackTimeoutRef.current) {
      clearTimeout(transferFallbackTimeoutRef.current);
      transferFallbackTimeoutRef.current = null;
    }

    // Clear idle watchdog
    if (watchdogIntervalRef.current) {
      clearInterval(watchdogIntervalRef.current);
      watchdogIntervalRef.current = null;
    }

    // Stop mic tracks
    if (micStreamRef.current) {
      micStreamRef.current.getTracks().forEach(track => track.stop());
      micStreamRef.current = null;
    }

    // Close audio contexts
    if (captureCtxRef.current && captureCtxRef.current.state !== 'closed') {
      captureCtxRef.current.close().catch(() => {});
      captureCtxRef.current = null;
    }
    if (playbackCtxRef.current && playbackCtxRef.current.state !== 'closed') {
      playbackCtxRef.current.close().catch(() => {});
      playbackCtxRef.current = null;
    }
    nextPlayTimeRef.current = 0;

    // Close WebSocket
    if (wsRef.current) {
      if (wsRef.current.readyState === WebSocket.OPEN) {
        try {
          wsRef.current.send(JSON.stringify({ close: true }));
        } catch {
          // ignore
        }
      }
      wsRef.current.close();
      wsRef.current = null;
    }

    agentTranscriptRef.current = '';
    userTranscriptRef.current = '';
    micMutedRef.current = false;
    suppressGreetingRef.current = false;
    transferTTSPlayingRef.current = false;
    awaitingTransferTurnRef.current = false;
    currentAuthorRef.current = 'Sam';
    isActiveRef.current = false;

    setState({
      isActive: false,
      isConnecting: false,
      isSpeaking: false,
      currentTranscript: '',
    });
  }, []);

  const startVoiceMode = useCallback(async (initialGreeting?: string) => {
    if (state.isActive || state.isConnecting) return;

    setState(prev => ({ ...prev, isConnecting: true }));

    // Mute mic if we need to play an initial greeting first
    micMutedRef.current = !!initialGreeting;
    suppressGreetingRef.current = !!initialGreeting;

    try {
      // 1. Open WebSocket
      const wsUrl = `${getWsUrl()}/ws/voice?session_id=${encodeURIComponent(sessionId)}`;
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      await new Promise<void>((resolve, reject) => {
        ws.onopen = () => resolve();
        ws.onerror = () => reject(new Error('WebSocket connection failed'));
        setTimeout(() => reject(new Error('WebSocket connection timeout')), 10000);
      });

      // 2. Set up capture AudioContext at 16kHz
      const captureCtx = new AudioContext({ sampleRate: 16000 });
      captureCtxRef.current = captureCtx;
      if (captureCtx.state === 'suspended') await captureCtx.resume();
      await captureCtx.audioWorklet.addModule('/audio-capture-processor.js');

      // 3. Get microphone stream
      const micStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
        },
      });
      micStreamRef.current = micStream;

      const micSource = captureCtx.createMediaStreamSource(micStream);
      const captureNode = new AudioWorkletNode(captureCtx, 'audio-capture-processor');

      // Wire: mic → worklet → WebSocket (muted during initial greeting)
      captureNode.port.onmessage = (event: MessageEvent) => {
        if (micMutedRef.current) return;
        if (ws.readyState === WebSocket.OPEN) {
          const base64Audio = arrayBufferToBase64(event.data);
          const liveRequest = {
            blob: {
              data: base64Audio,
              mime_type: 'audio/pcm;rate=16000',
            },
          };
          ws.send(JSON.stringify(liveRequest));
        }
      };

      micSource.connect(captureNode);
      captureNode.connect(captureCtx.destination);

      // 4. Set up playback AudioContext at 24kHz (no AudioWorklet — use BufferSource)
      const playbackCtx = new AudioContext({ sampleRate: 24000 });
      playbackCtxRef.current = playbackCtx;
      if (playbackCtx.state === 'suspended') await playbackCtx.resume();
      nextPlayTimeRef.current = 0;

      console.log('[voice] Playback context created, state:', playbackCtx.state, 'sampleRate:', playbackCtx.sampleRate);

      // 5. Handle incoming events from the server
      let audioChunkCount = 0;
      let transcriptEventCount = 0;

      ws.onmessage = (event: MessageEvent) => {
        lastEventTimeRef.current = Date.now();
        try {
          const data = JSON.parse(event.data);

          // Backend keepalive ping — just feed the watchdog timer, skip processing
          if (data.ping) return;

          // Backend-driven agent transfer (voice switching)
          if (data.agentTransfer) {
            const { from, to, message } = data.agentTransfer;
            console.log(`[voice] Agent transfer: ${from} → ${to}`);
            currentAuthorRef.current = to;

            if (transferFallbackTimeoutRef.current) {
              clearTimeout(transferFallbackTimeoutRef.current);
            }

            // Mute mic immediately to prevent echo feedback
            micMutedRef.current = true;
            transferTTSPlayingRef.current = true;
            awaitingTransferTurnRef.current = true;
            agentTranscriptRef.current = '';
            setState(prev => ({ ...prev, currentTranscript: '' }));

            transferFallbackTimeoutRef.current = setTimeout(() => {
              console.warn('[voice] Transfer turnComplete timeout — clearing transfer wait state');
              awaitingTransferTurnRef.current = false;
              suppressGreetingRef.current = false;
              transferFallbackTimeoutRef.current = null;
            }, 15000);

            // Wait for any queued agent audio to finish playing before
            // starting the TTS announcement so we don't talk over Sam's goodbye.
            const ctx = playbackCtxRef.current;
            const remainingAudio = ctx
              ? Math.max(0, nextPlayTimeRef.current - ctx.currentTime)
              : 0;
            const delayMs = Math.ceil(remainingAudio * 1000) + 150; // +150ms buffer

            // Wait until ALL three conditions are met before unmuting:
            // 1. TTS announcement has finished (we're in onend)
            // 2. All queued agent audio has finished playing
            // 3. The new agent's first turnComplete has been received
            // This prevents the mic from picking up the new agent's greeting.
            const safeUnmuteStartTime = Date.now();
            const safeUnmute = () => {
              const ctx = playbackCtxRef.current;
              const audioStillPlaying = ctx && nextPlayTimeRef.current > ctx.currentTime + 0.5;
              if (audioStillPlaying || awaitingTransferTurnRef.current) {
                // Fail-safe: force unmute after 15s to avoid permanent mute
                if (Date.now() - safeUnmuteStartTime > 15000) {
                  console.warn('[voice] Transfer safe-unmute timeout — forcing unmute');
                } else {
                  setTimeout(safeUnmute, 200);
                  return;
                }
              }
              transferTTSPlayingRef.current = false;
              micMutedRef.current = false;
              console.log('[voice] Transfer complete — mic unmuted');
            };

            const playAnnouncement = () => {
              if ('speechSynthesis' in window && message) {
                const utterance = new SpeechSynthesisUtterance(message);
                utterance.rate = 1.1;
                utterance.volume = 0.8;
                utterance.onend = () => safeUnmute();
                utterance.onerror = () => safeUnmute();
                window.speechSynthesis.speak(utterance);
              } else {
                safeUnmute();
              }
            };

            if (delayMs > 150) {
              console.log(`[voice] Waiting ${delayMs}ms for agent audio to finish before transfer TTS`);
              setTimeout(playAnnouncement, delayMs);
            } else {
              playAnnouncement();
            }

            callbacks?.onAgentTransfer?.(to);
            return;
          }

          // Tool result forwarded from backend (search results with markdown links)
          if (data.voiceToolResult) {
            const { agent, message, toolName } = data.voiceToolResult;
            callbacks?.onToolResult?.(agent || currentAuthorRef.current, message, toolName);
            return;
          }

          // Backend signals conversation is complete
          if (data.conversationEnded) {
            console.log('[voice] Conversation ended by agent');
            callbacks?.onConversationEnd?.();
            cleanup();
            return;
          }

          // Track author changes for transcript labeling (transfers handled by agentTransfer event)
          if (data.author && data.author !== currentAuthorRef.current) {
            console.log(`[voice] Agent author change: ${currentAuthorRef.current} → ${data.author}`);
            currentAuthorRef.current = data.author;
          }

          // Extract and play audio from inlineData
          if (data.content?.parts) {
            for (const part of data.content.parts) {
              if (part.inlineData?.data && part.inlineData?.mimeType?.startsWith('audio/')) {
                audioChunkCount++;
                const pcmBytes = base64ToUint8Array(part.inlineData.data);
                if (audioChunkCount <= 3) {
                  console.log(`[voice] Audio chunk #${audioChunkCount}: ${pcmBytes.length} bytes, mime=${part.inlineData.mimeType}, ctx.state=${playbackCtxRef.current?.state}`);
                }
                playPCM(pcmBytes);
                setState(prev => ({ ...prev, isSpeaking: true }));
              }
            }
          }

          // Interrupted / turnComplete are mutually exclusive with transcription
          // processing — a single event can carry both flags AND transcription
          // data, so we must not process transcription after finalizing.
          if (data.interrupted) {
            // User interrupted the agent — finalize partial agent transcript
            if (agentTranscriptRef.current && !suppressGreetingRef.current) {
              callbacks?.onAgentTranscript?.(agentTranscriptRef.current, true);
            }
            agentTranscriptRef.current = '';
            suppressGreetingRef.current = false;
            setState(prev => ({ ...prev, isSpeaking: false, currentTranscript: '' }));
          } else if (data.turnComplete) {
            // Signal that the new agent's greeting turn has completed.
            // safeUnmute() polls on this flag before unmuting the mic.
            if (awaitingTransferTurnRef.current) {
              console.log('[voice] New agent greeting turn complete — allowing unmute');
              awaitingTransferTurnRef.current = false;
            }
            if (transferFallbackTimeoutRef.current) {
              clearTimeout(transferFallbackTimeoutRef.current);
              transferFallbackTimeoutRef.current = null;
            }
            // Unmute mic after the initial greeting finishes, but NOT during
            // a transfer TTS — the TTS onend callback handles unmuting then.
            if (micMutedRef.current && !transferTTSPlayingRef.current) {
              console.log('[voice] Initial greeting done — unmuting mic');
              micMutedRef.current = false;
            }
            // Turn complete — finalize agent transcript
            console.log(`[voice] Turn complete. Audio chunks: ${audioChunkCount}, Transcript events: ${transcriptEventCount}`);
            audioChunkCount = 0;
            transcriptEventCount = 0;
            setState(prev => ({ ...prev, isSpeaking: false, currentTranscript: '' }));
            if (agentTranscriptRef.current && !suppressGreetingRef.current) {
              console.log(`[voice] Finalizing agent transcript (${agentTranscriptRef.current.length} chars)`);
              callbacks?.onAgentTranscript?.(agentTranscriptRef.current, true);
            }
            agentTranscriptRef.current = '';
            // Stop suppressing after the greeting turn completes
            suppressGreetingRef.current = false;
          } else {
            // Output transcription (agent speaking)
            if (data.outputTranscription?.text) {
              transcriptEventCount++;
              if (awaitingTransferTurnRef.current && transferFallbackTimeoutRef.current) {
                clearTimeout(transferFallbackTimeoutRef.current);
                transferFallbackTimeoutRef.current = null;
              }
              // Finalize pending user transcript when agent starts speaking
              if (userTranscriptRef.current) {
                console.log(`[voice] Finalizing user transcript (${userTranscriptRef.current.length} chars)`);
                callbacks?.onUserTranscript?.(userTranscriptRef.current, true);
                userTranscriptRef.current = '';
              }
              // finished=true → text is the complete utterance, REPLACE accumulated
              // finished=false/undefined → text is a delta chunk, APPEND
              if (data.outputTranscription.finished) {
                agentTranscriptRef.current = data.outputTranscription.text;
              } else {
                agentTranscriptRef.current += data.outputTranscription.text;
              }
              if (!suppressGreetingRef.current) {
                setState(prev => ({ ...prev, currentTranscript: agentTranscriptRef.current }));
                // Don't mark as isFinal here — turnComplete handles finalization
                callbacks?.onAgentTranscript?.(agentTranscriptRef.current, false);
              }
            }

            // Input transcription (user speaking)
            if (data.inputTranscription?.text) {
              // finished=true → text is the complete utterance, REPLACE and finalize
              // finished=false/undefined → text is a delta chunk, APPEND
              if (data.inputTranscription.finished) {
                userTranscriptRef.current = data.inputTranscription.text;
                callbacks?.onUserTranscript?.(userTranscriptRef.current, true);
                userTranscriptRef.current = '';
              } else {
                userTranscriptRef.current += data.inputTranscription.text;
                callbacks?.onUserTranscript?.(userTranscriptRef.current, false);
              }
            }
          }


        } catch (e) {
          console.error('[voice] Event processing error:', e, 'raw:', event.data.substring(0, 200));
        }
      };

      ws.onclose = (ev: CloseEvent) => {
        console.log(`[voice] WebSocket closed: code=${ev.code} reason=${ev.reason}`);
        // Finalize any pending transcripts (for unexpected disconnects)
        if (userTranscriptRef.current) {
          callbacks?.onUserTranscript?.(userTranscriptRef.current, true);
        }
        if (agentTranscriptRef.current && !suppressGreetingRef.current) {
          callbacks?.onAgentTranscript?.(agentTranscriptRef.current, true);
        }
        // Surface unexpected close to user (1000 = normal close)
        if (ev.code !== 1000 && isActiveRef.current) {
          const reason = ev.reason || `Connection lost (code ${ev.code})`;
          callbacks?.onError?.(reason);
        }
        cleanup();
      };

      ws.onerror = () => {
        callbacks?.onError?.('Voice connection error');
        cleanup();
      };

      // Start idle watchdog: if no events for 90s, surface error and cleanup.
      // Agent transfers involve tool calls (search_flights, etc.) that can take
      // 30-60s with no events — the previous 30s timeout was too aggressive.
      lastEventTimeRef.current = Date.now();
      watchdogIntervalRef.current = setInterval(() => {
        const elapsed = Date.now() - lastEventTimeRef.current;
        if (elapsed > 90_000) {
          console.warn('[voice] Idle watchdog triggered — no events for 90s');
          callbacks?.onError?.('Voice connection appears stale — reconnecting may help');
          cleanup();
        }
      }, 15_000);

      // Send initial greeting prompt so Sam speaks first (mic is muted until turnComplete)
      if (initialGreeting && ws.readyState === WebSocket.OPEN) {
        console.log('[voice] Sending initial greeting prompt to Live API');
        ws.send(JSON.stringify({
          content: {
            role: 'user',
            parts: [{ text: initialGreeting }],
          },
        }));
      }

      isActiveRef.current = true;
      setState({
        isActive: true,
        isConnecting: false,
        isSpeaking: false,
        currentTranscript: '',
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to start voice mode';
      callbacks?.onError?.(message);
      cleanup();
    }
  }, [sessionId, state.isActive, state.isConnecting, callbacks, cleanup]);

  const stopVoiceMode = useCallback(() => {
    console.log('[voice] Stopping voice mode');
    // Finalize any pending transcripts before cleanup, and clear refs
    // to prevent ws.onclose from re-finalizing (causing duplicates)
    if (userTranscriptRef.current) {
      callbacksRef.current?.onUserTranscript?.(userTranscriptRef.current, true);
      userTranscriptRef.current = '';
    }
    if (agentTranscriptRef.current) {
      callbacksRef.current?.onAgentTranscript?.(agentTranscriptRef.current, true);
      agentTranscriptRef.current = '';
    }
    cleanup();
  }, [cleanup]);

  return {
    ...state,
    startVoiceMode,
    stopVoiceMode,
  };
}
