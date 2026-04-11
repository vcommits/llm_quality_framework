/**
 * GHIDORAH // CORE // ASSET_MANAGER
 * Handles hot-swapping of UI mood tokens (fonts, backgrounds, GIFs).
 */
export class AssetManager {
    constructor() {
        this.moods = [
            {
                id: 'noir',
                header: "'Arial Black', sans-serif",
                data: "'Courier New', monospace",
                bg: 'none',
                gif: 'none'
            },
            {
                id: 'ukiyo',
                header: 'Kamikaze',
                data: 'Ninja Kage',
                bg: 'url("/assets/visuals/ukiyo_grid.webp")',
                gif: 'none'
            },
            {
                id: 'glitch',
                header: 'Akihabored',
                data: 'Space Mono',
                bg: 'rgba(20, 0, 0, 0.2)',
                gif: 'url("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJqZ3R5Z3R5Z3R5Z3R5Z3R5Z3R5Z3R5Z3R5Z3R5Z3R5JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7TKMGpxx8G4/giphy.gif")'
            }
        ];
        this.idx = 0;
    }

    cycle() {
        this.idx = (this.idx + 1) % this.moods.length;
        const mood = this.moods[this.idx];
        const root = document.documentElement;

        root.style.setProperty('--font-header', mood.header);
        root.style.setProperty('--font-data', mood.data);
        root.style.setProperty('--bg-texture', mood.bg);
        root.style.setProperty('--bg-gif', mood.gif);

        console.log(`SENTRY: Auditioning Mood -> ${mood.id.toUpperCase()}`);
    }
}