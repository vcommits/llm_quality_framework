/**
 * GHIDORAH SIGNAL BRIDGE (Node X)
 * Strictly OOP: Handles authenticated API communication.
 */
class NetworkClient {
    constructor(baseUrl = 'http://127.0.0.1:8000') {
        this.baseUrl = baseUrl;
    }

    async call(endpoint, payload) {
        const url = `${this.baseUrl}${endpoint}`;
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (!response.ok) throw new Error(`SIGNAL_INTERRUPTED: ${response.status}`);
            return response; 
        } catch (error) {
            console.error("FATAL_LINK_FAILURE:", error);
            throw error;
        }
    }
    
    async get(endpoint) {
        const url = `${this.baseUrl}${endpoint}`;
        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error(`SIGNAL_INTERRUPTED: ${response.status}`);
            return response; 
        } catch (error) {
            console.error("FATAL_LINK_FAILURE:", error);
            throw error;
        }
    }
}
