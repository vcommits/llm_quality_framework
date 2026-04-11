/**
 * SENTRY SOUND MANAGER: Zero-latency audio triggers.
 * Pre-loads all UI sound effects into an AudioContext for instant playback.
 */
class SentrySoundManager {
    constructor() {
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        this.soundBuffers = {};
        this.sounds = {
            'handshake': '../assets/audio/handshake.wav',
            'boundary_violation': '../assets/audio/alert.wav',
            'click': '../assets/audio/click.wav',
            'transition': '../assets/audio/whoosh.wav',
            'punch': '../assets/audio/punch.wav'
        };
    }

    async preloadSounds() {
        for (const key in this.sounds) {
            try {
                const response = await fetch(this.sounds[key]);
                const arrayBuffer = await response.arrayBuffer();
                this.soundBuffers[key] = await this.audioContext.decodeAudioData(arrayBuffer);
            } catch (e) {
                console.error(`Failed to load sound: ${key}`, e);
            }
        }
    }

    playSound(name) {
        if (this.soundBuffers[name]) {
            const source = this.audioContext.createBufferSource();
            source.buffer = this.soundBuffers[name];
            source.connect(this.audioContext.destination);
            source.start(0);
        }
    }
}
