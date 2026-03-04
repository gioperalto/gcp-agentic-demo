/**
 * AudioWorklet processor for capturing microphone input at 16kHz.
 * Converts Float32 samples to Int16 PCM and buffers ~128ms (2048 samples)
 * before posting to the main thread.
 */
class AudioCaptureProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this._buffer = new Int16Array(2048);
    this._offset = 0;
  }

  process(inputs) {
    const input = inputs[0];
    if (!input || !input[0]) return true;

    const samples = input[0];
    for (let i = 0; i < samples.length; i++) {
      // Clamp and convert Float32 [-1, 1] to Int16 [-32768, 32767]
      const s = Math.max(-1, Math.min(1, samples[i]));
      this._buffer[this._offset++] = s < 0 ? s * 0x8000 : s * 0x7fff;

      if (this._offset >= this._buffer.length) {
        // Send a copy of the buffer to the main thread
        this.port.postMessage(this._buffer.buffer.slice(0));
        this._offset = 0;
      }
    }

    return true;
  }
}

registerProcessor('audio-capture-processor', AudioCaptureProcessor);
