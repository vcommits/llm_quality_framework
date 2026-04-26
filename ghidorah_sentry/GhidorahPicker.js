/**
 * 🐉 Ghidorah Mesh: Modular Picker Component (v1.1.0)
 * * Merged logic for Firehose discovery and contextual CTA.
 */
class GhidorahPicker {
    constructor(mountId, apiEndpoint) {
        this.mountPoint = document.getElementById(mountId);
        this.apiEndpoint = apiEndpoint;
        this.models = [];
        this.selectedModel = null;

        this.render();
        this.cacheElements();
        this.bindEvents();
        this.init();
    }

    render() {
        this.mountPoint.innerHTML = `
            <div class="ghid-picker-v2" style="display: flex; flex-direction: column; gap: 1rem; background: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155;">
                <div class="field-group">
                    <label style="display:block; font-size: 0.75rem; font-weight:bold; margin-bottom:0.4rem; color: #38bdf8;">1. PROVIDER</label>
                    <select id="ghid-provider" style="width:100%; padding:12px; background:#0f172a; color:#fff; border:1px solid #334155; border-radius:8px; outline:none;"></select>
                </div>
                <div class="field-group">
                    <label style="display:block; font-size: 0.75rem; font-weight:bold; margin-bottom:0.4rem; color: #38bdf8;">2. TYPE FILTER</label>
                    <select id="ghid-filter" disabled style="width:100%; padding:12px; background:#0f172a; color:#fff; border:1px solid #334155; border-radius:8px; outline:none;">
                        <option value="all">-- ALL MODELS --</option>
                        <option value="chat">📝 TEXT / CHAT</option>
                        <option value="vision">👁️ VISION / VL</option>
                        <option value="audio">🎧 SENSORY / TTS</option>
                        <option value="coding">💻 CODING / DEV</option>
                        <option value="embedding">🧬 EMBEDDING</option>
                    </select>
                </div>
                <div class="field-group">
                    <label style="display:block; font-size: 0.75rem; font-weight:bold; margin-bottom:0.4rem; color: #38bdf8;">3. TARGET MODEL</label>
                    <select id="ghid-model" disabled style="width:100%; padding:12px; background:#0f172a; color:#fff; border:1px solid #334155; border-radius:8px; outline:none;"></select>
                </div>
                <button id="ghid-cta" style="display:none; width:100%; padding:16px; border-radius:8px; border:none; background:#f59e0b; color:#000; font-weight:800; cursor:pointer; text-transform:uppercase;">INJECT PAYLOAD</button>
                <div id="ghid-status" style="display:none; font-family: monospace; font-size: 0.75rem; color: #10b981;"></div>
            </div>
        `;
    }

    cacheElements() {
        this.el = {
            provider: document.getElementById('ghid-provider'),
            filter: document.getElementById('ghid-filter'),
            model: document.getElementById('ghid-model'),
            cta: document.getElementById('ghid-cta'),
            status: document.getElementById('ghid-status')
        };
    }

    bindEvents() {
        this.el.provider.onchange = (e) => this.fetchModels(e.target.value);
        this.el.filter.onchange = () => this.applyFilter();
        this.el.model.onchange = (e) => this.stageModel(e.target.value);
    }

    async init() {
        try {
            const res = await fetch(`${this.apiEndpoint}/api/v1/providers`);
            const providers = await res.json();
            let html = '<option value="">-- CHOOSE PROVIDER --</option>';
            providers.forEach(p => html += `<option value="${p}">${p.toUpperCase()}</option>`);
            this.el.provider.innerHTML = html;
        } catch (err) { this.el.provider.innerHTML = '<option>MESH OFFLINE</option>'; }
    }

    async fetchModels(provider) {
        if (!provider) return;
        this.el.model.innerHTML = '<option>HYDRATING...</option>';
        try {
            const res = await fetch(`${this.apiEndpoint}/api/v1/manifest/${provider}`);
            const data = await res.json();
            this.models = data.models || [];
            this.el.filter.disabled = false;
            this.el.model.disabled = false;
            this.applyFilter();
        } catch (err) { console.error(err); }
    }

    applyFilter() {
        const type = this.el.filter.value;
        const filtered = this.models.filter(m => type === "all" || m.type === type);
        let html = `<option value="">-- ${filtered.length} TARGETS FOUND --</option>`;
        filtered.forEach(m => html += `<option value="${m.model_id}">${m.model_id}</option>`);
        this.el.model.innerHTML = html;
        this.el.cta.style.display = 'none';
    }

    stageModel(modelId) {
        if (!modelId) return;
        this.selectedModel = this.models.find(m => m.model_id === modelId);
        this.el.cta.style.display = 'block';
        this.el.status.style.display = 'block';
        this.el.status.innerText = `LOCKED: [${this.selectedModel.provider}] > ${modelId}`;

        // Contextual CTA
        const t = this.selectedModel.type;
        if (t === 'coding') this.el.cta.innerText = "EXECUTE CODE EVAL";
        else if (t === 'vision') this.el.cta.innerText = "INJECT VISION PAYLOAD";
        else this.el.cta.innerText = "INJECT TEXT PAYLOAD";
    }
}