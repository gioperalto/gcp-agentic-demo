/**
 * AudioWorklet processor for playing back PCM audio from the Gemini Live API.
 * Receives Int16 PCM at 24kHz from the main thread and outputs Float32 to speakers.
 * Uses a ring buffer for smooth, gap-free playback.
 */
class AudioPlaybackProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    // Ring buffer: ~2 seconds at 24kHz
    this._ringBuffer = new Float32Array(48000);
    this._writePos = 0;
    this._readPos = 0;
    this._buffered = 0;

    this.port.onmessage = (event) => {
      const int16Data = new Int16Array(event.data);
      for (let i = 0; i < int16Data.length; i++) {
        // Convert Int16 to Float32
        this._ringBuffer[this._writePos] = int16Data[i] / 32768;
        this._writePos = (this._writePos + 1) % this._ringBuffer.length;
        this._buffered++;
      }
    };
  }

  process(outputs) {
    const output = outputs[0];
    if (!output || !output[0]) return true;

    const channel = output[0];
    for (let i = 0; i < channel.length; i++) {
      if (this._buffered > 0) {
        channel[i] = this._ringBuffer[this._readPos];
        this._readPos = (this._readPos + 1) % this._ringBuffer.length;
        this._buffered--;
      } else {
        channel[i] = 0; // Silence when buffer is empty
      }
    }

    return true;
  }
}

registerProcessor('audio-playback-processor', AudioPlaybackProcessor);
