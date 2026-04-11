/**
 * GHIDORAH // CORE // MATCHMAKER
 * Handles the 4-tier discovery logic: Provider -> Type -> Tier -> Model.
 */
export class Matchmaker {
    constructor(manifestUrl) {
        this.manifestUrl = manifestUrl;
        this.models = [];
        this.selection = { provider: null, type: null, tier: null, model: null };
        this.activeWeightclass = null; // Locks after first fighter commitment
    }

    async hydrate() {
        try {
            const response = await fetch(this.manifestUrl);
            const data = await response.json();
            // FILTER: Only show 'online' models (No Ghost Summons)
            this.models = (data.models || []).filter(m => m.status === 'online');
            return true;
        } catch (e) {
            console.error("SENTRY: Manifest Hydration Error.", e);
            return false;
        }
    }

    getOptions(level) {
        const s = this.selection;
        // Filter based on previous choices and Weightclass Lock
        const pool = this.models.filter(m =>
            (!this.activeWeightclass || m.weightclass === this.activeWeightclass) &&
            (level === 'provider' || m.provider === s.provider) &&
            (level === 'type' || (m.provider === s.provider && m.type === s.type))
        );

        if (level === 'provider') return [...new Set(pool.map(m => m.provider))];
        if (level === 'type') return [...new Set(pool.filter(m => m.provider === s.provider).map(m => m.type))];
        if (level === 'tier') return [...new Set(pool.filter(m => m.provider === s.provider && m.type === s.type).map(m => m.tier))];
        if (level === 'model') return pool.filter(m => m.provider === s.provider && m.type === s.type && m.tier === s.tier);

        return [];
    }

    reset() {
        this.selection = { provider: null, type: null, tier: null, model: null };
    }
}