class AudioProcessor extends AudioWorkletProcessor {
    process(inputs) {
        const inputChannel = inputs[0][0];
        if (inputChannel) {
            const pcmData = this.to16BitPCM(inputChannel);
            this.port.postMessage(pcmData, [pcmData.buffer]);
        }
        return true;
    }

    to16BitPCM(input) {
        const dataLength = input.length;
        const buffer = new ArrayBuffer(dataLength * 2);
        const dataView = new DataView(buffer);
        for (let i = 0; i < dataLength; i++) {
            const s = Math.max(-1, Math.min(1, input[i]));
            dataView.setInt16(i * 2, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
        }
        return new Uint8Array(buffer);
    }
}

registerProcessor('audio-processor', AudioProcessor);