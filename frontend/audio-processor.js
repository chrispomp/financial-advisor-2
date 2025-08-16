// This AudioWorkletProcessor is responsible for capturing raw audio data
// and converting it into 16-bit PCM format, which is required by the Gemini Live API.
class AudioProcessor extends AudioWorkletProcessor {
    process(inputs) {
        // Get the audio data from the first channel.
        const inputChannel = inputs[0][0];
        if (inputChannel) {
            // Convert the floating-point audio data to 16-bit PCM.
            const pcmData = this.to16BitPCM(inputChannel);
            // Post the raw PCM data back to the main thread to be sent over the WebSocket.
            this.port.postMessage(pcmData);
        }
        // Return true to keep the processor alive.
        return true;
    }

    // Converts a Float32Array of audio samples to a 16-bit PCM ArrayBuffer.
    to16BitPCM(input) {
        const dataLength = input.length;
        const buffer = new ArrayBuffer(dataLength * 2);
        const dataView = new DataView(buffer);
        for (let i = 0; i < dataLength; i++) {
            // Clamp the sample to the [-1, 1] range and scale to 16-bit integer range.
            const s = Math.max(-1, Math.min(1, input[i]));
            const intSample = s < 0 ? s * 0x8000 : s * 0x7FFF;
            dataView.setInt16(i * 2, intSample, true); // true for little-endian
        }
        return buffer;
    }
}

registerProcessor('audio-processor', AudioProcessor);