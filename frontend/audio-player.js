class AudioPlayerProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
        // Use a Float32Array for the buffer, which is what the audio output needs.
        this._buffer = new Float32Array();

        // Listen for messages from the main thread containing PCM data.
        this.port.onmessage = (event) => {
            const pcmData = event.data.pcmData;
            if (pcmData) {
                // Convert the incoming 16-bit PCM data to 32-bit Float data and enqueue it.
                const floatData = this.convertPCMToInt16ToFloat32(pcmData);
                this.enqueue(floatData);
            }
        };
    }

    /**
     * Converts a 16-bit PCM Int16Array to a 32-bit Float32Array.
     * The Web Audio API requires samples to be in the -1.0 to 1.0 range.
     */
    convertPCMToInt16ToFloat32(pcmData) {
        const floatData = new Float32Array(pcmData.length);
        for (let i = 0; i < pcmData.length; i++) {
            // Normalize the 16-bit integer to the float range.
            floatData[i] = pcmData[i] / 32768.0;
        }
        return floatData;
    }

    /**
     * Appends new audio data to the internal buffer.
     */
    enqueue(floatData) {
        const newBuffer = new Float32Array(this._buffer.length + floatData.length);
        newBuffer.set(this._buffer, 0);
        newBuffer.set(floatData, this._buffer.length);
        this._buffer = newBuffer;
    }

    /**
     * This method is called by the audio system to process audio data.
     */
    process(inputs, outputs) {
        const outputChannel = outputs[0][0];
        const bufferSize = outputChannel.length;

        // If there is data in our buffer, copy it to the output channel.
        if (this._buffer.length > 0) {
            const chunk = this._buffer.subarray(0, bufferSize);
            outputChannel.set(chunk);

            // Remove the chunk from the buffer.
            this._buffer = this._buffer.subarray(chunk.length);
        }

        // Return true to keep the processor alive.
        return true;
    }
}

registerProcessor('audio-player-processor', AudioPlayerProcessor);
