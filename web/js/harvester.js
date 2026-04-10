/**
 * Harvester: Standardizes raw model responses into Telemetry.
 */
class Harvester {
    constructor() {}

    /**
     * Standardizes raw model responses into Telemetry.
     * @param {Object} data - The parsed JSON response from the server.
     * @param {Headers} headers - Optional fetch response headers.
     */
    process(data, headers = null) {
        return {
            fingerprint: headers?.get('x-system-fingerprint') || 'UNKNOWN',
            finish_reason: data.choices?.[0]?.finish_reason || 'stop',
            latency: headers?.get('x-request-latency') || '0ms',
            burn: {
                total: data.usage?.total_tokens || 0,
                prompt: data.usage?.prompt_tokens || 0,
                completion: data.usage?.completion_tokens || 0,
                cost: this.calculateCost(data.usage, data.model)
            },
            raw: data // For the "Postman JSON" foldout
        };
    }

    calculateCost(usage, model) {
        // Logic to return the 💵 stack emoji value
        if(!usage) return "0.0000";
        return (usage.total_tokens * 0.000002).toFixed(4);
    }
}
