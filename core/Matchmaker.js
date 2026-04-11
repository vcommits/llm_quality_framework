/**
 * Matchmaker Class
 *
 * Handles the 4-tier discovery logic for LLM models based on the OOP-GLASSDESK architecture.
 * It filters models from a manifest to prevent "Ghost Model" summons and ensures "Like-for-Like" combat.
 */
class Matchmaker {
    constructor(manifest) {
        this.manifest = manifest;
        this.activeWeightclass = null;
    }

    /**
     * Filters models from the manifest where status is 'online'.
     * @returns {Array} A list of online models.
     */
    hydrate() {
        return this.manifest.filter(model => model.status === 'online');
    }

    /**
     * Gets a unique list of providers from the online models.
     * @returns {Array<string>}
     */
    getProviders() {
        const onlineModels = this.hydrate();
        const providers = new Set(onlineModels.map(model => model.provider));
        return [...providers];
    }

    /**
     * Gets a unique list of types for a given provider.
     * @param {string} provider
     * @returns {Array<string>}
     */
    getTypes(provider) {
        const onlineModels = this.hydrate();
        const types = new Set(
            onlineModels
                .filter(model => model.provider === provider)
                .map(model => model.type)
        );
        return [...types];
    }

    /**
     * Gets a unique list of tiers for a given provider and type.
     * @param {string} provider
     * @param {string} type
     * @returns {Array<string>}
     */
    getTiers(provider, type) {
        const onlineModels = this.hydrate();
        const tiers = new Set(
            onlineModels
                .filter(model => model.provider === provider && model.type === type)
                .map(model => model.tier)
        );
        return [...tiers];
    }

    /**
     * Gets models based on the selected filters.
     * If an activeWeightclass is set, it further filters by that.
     * @param {string} provider
     * @param {string} type
     * @param {string} tier
     * @returns {Array}
     */
    getModels(provider, type, tier) {
        let models = this.hydrate().filter(model =>
            model.provider === provider &&
            model.type === type &&
            model.tier === tier
        );

        if (this.activeWeightclass) {
            models = models.filter(model => model.type === this.activeWeightclass);
        }

        return models;
    }

    /**
     * Locks the arena to a specific weightclass (type).
     * @param {string} weightclass
     */
    lockWeightclass(weightclass) {
        this.activeWeightclass = weightclass;
        console.log(`Weightclass locked to: ${this.activeWeightclass}`);
    }

    /**
     * Resets the weightclass lock.
     */
    resetWeightclass() {
        this.activeWeightclass = null;
        console.log('Weightclass lock has been reset.');
    }
}
