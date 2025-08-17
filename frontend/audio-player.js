class AudioPlayerProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
        this.buffer = [];
        this.isPlaying = false;
    }

    process(inputs, outputs) {
        const outputChannel = outputs[0][0];
        if (this.isPlaying) {
            const bufferSize = outputChannel.length;
            const buffer = this.buffer.splice(0, bufferSize);
            if (buffer.length > 0) {
                outputChannel.set(buffer);
            } else {
                this.isPlaying = false;
            }
        }
        return true;
    }

    start() {
        this.isPlaying = true;
    }

    stop() {
        this.isPlaying = false;
        this.buffer = [];
    }

    enqueue(data) {
        this.buffer.push(...data);
        if (!this.isPlaying) {
            this.start();
        }
    }
}

registerProcessor('audio-player-processor', AudioPlayerProcessor);
