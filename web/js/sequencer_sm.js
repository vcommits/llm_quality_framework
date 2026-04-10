/**
 * SEQUENCE CONTROLLER: "Tape Deck" State Machine
 * Handles playhead, parameters, and the MiM pause logic.
 */
class SequenceController {
    constructor() {
        this.tracks = [];         
        this.playhead = 0;        
        this.isPlaying = false;
        this.parameters = {};     
        this.isInterceptOn = false;
        this.network = null; // Injected NetworkClient instance
    }

    load(ghidSession, networkClient) {
        this.tracks = ghidSession.sequence;
        this.parameters = ghidSession.parameters || {};
        this.playhead = 0;
        this.network = networkClient;
        console.log("Tape loaded.", this.tracks.length, "turns.");
    }

    async play() {
        this.isPlaying = true;
        while (this.playhead < this.tracks.length && this.isPlaying) {
            const success = await this.step();
            if (!success) break; 
        }
        this.isPlaying = false;
    }

    async step() {
        let currentTrack = this.tracks[this.playhead];
        
        // 1. Parameter Injection 
        let processedPayload = this.injectParams(currentTrack.prompt);

        // 2. MiM Gate
        if (this.isInterceptOn) {
            this.isPlaying = false; 
            window.triggerMiMEditor(processedPayload); 
            return false; 
        }

        // 3. Dispatch
        return await this.dispatch(processedPayload);
    }

    injectParams(text) {
        return text.replace(/{{(\w+)}}/g, (match, key) => {
            return this.parameters[key] || match;
        });
    }

    async dispatch(payload) {
        // Hands off to the UI dispatcher which handles the /api/v1/dispatch call
        // and manages rendering to the chat window.
        // We assume `window.dispatchToLiveModel` returns true/false on success.
        const success = await window.dispatchToLiveModel(payload);
        if (success) {
            this.playhead++;
            return true;
        }
        return false;
    }
}
