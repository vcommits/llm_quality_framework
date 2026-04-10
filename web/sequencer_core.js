class SequenceController {
    constructor() {
        this.tracks = [];         // The loaded session turns
        this.playhead = 0;        // Current turn index
        this.isPlaying = false;
        this.parameters = {};     // e.g., { "target_model": "gemini-2.5" }
        this.isInterceptOn = false;
    }

    load(ghidSession) {
        this.tracks = ghidSession.sequence;
        this.parameters = ghidSession.parameters || {};
        this.playhead = 0;
        this.updateUI();
    }

    // The "Smart Rehash" Loop
    async play() {
        this.isPlaying = true;
        while (this.playhead < this.tracks.length && this.isPlaying) {
            const success = await this.step();
            if (!success) break; // Pause on error or drop
        }
        this.isPlaying = false;
    }

    async step() {
        let currentTrack = this.tracks[this.playhead];

        // 1. Parameter Injection (The "Smart" part)
        let processedPayload = this.injectParams(currentTrack.prompt);

        // 2. The MiM Gate (BurpSuite Pause)
        if (this.isInterceptOn) {
            this.isPlaying = false; // Pause automation for manual intervention
            triggerMiMEditor(processedPayload);
            return false;
        }

        // 3. Dispatch to Target
        const result = await this.dispatch(processedPayload);

        if (result.success) {
            this.playhead++;
            updatePostman(result.metadata);
            addTurnToVault(processedPayload, result.response, result.metadata);
            return true;
        }
        return false;
    }

    injectParams(text) {
        return text.replace(/{{(\w+)}}/g, (match, key) => {
            return this.parameters[key] || match;
        });
    }

    async dispatch(payload) {
        // Hits the Node X FastAPI /api/v1/mutate or direct Model API
        const response = await fetch('/api/v1/dispatch', {
            method: 'POST',
            body: JSON.stringify({ payload: payload, model: this.parameters.target_model })
        });
        return await response.json();
    }
}