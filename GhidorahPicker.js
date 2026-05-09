class GhidorahPicker {
    constructor(mountId, apiEndpoint) {
        this.mountPoint = document.getElementById(mountId);
        this.apiEndpoint = apiEndpoint || "http://100.101.24.26:8080";
        this.models = [];
        this.selectedProviderType = "maker";
        this.render();
        this.cacheElements();
        this.bindEvents();
        this.init();
    }

    render() {
        this.mountPoint.innerHTML = `
            <div class="ghid-picker-v2" style="display: flex; flex-direction: column; gap: 1rem; background: #0f172a; padding: 20px; border-radius: 12px; border: 1px solid #1e293b;">
                <div id="ghid-status-log" style="font-family: monospace; font-size: 0.75rem; font-weight: bold; margin-bottom: 10px; display: none;"></div>
                
                <label style="font-size: 0.7rem; color: #38bdf8; font-weight:bold; text-transform:uppercase;">1. Provider</label>
                <select id="ghid-provider" style="width:100%; padding:10px; background:#020617; color:#fff; border:1px solid #334155; border-radius:8px;"></select>
                
                <label style="font-size: 0.7rem; color: #38bdf8; font-weight:bold; text-transform:uppercase;">2. Filter Class</label>
                <select id="ghid-filter" disabled style="width:100%; padding:10px; background:#020617; color:#fff; border:1px solid #334155; border-radius:8px;">
                    <option value="all">-- ALL MODELS --</option>
                    <option value="chat">📝 TEXT / CHAT</option>
                    <option value="vision">👁️ VISION</option>
                    <option value="audio">🎧 SENSORY</option>
                    <option value="coding">💻 CODING</option>
                    <option value="embedding">🧬 EMBEDDING</option>
                </select>

                <label style="font-size: 0.7rem; color: #38bdf8; font-weight:bold; text-transform:uppercase;">3. Target</label>
                <select id="ghid-model" disabled style="width:100%; padding:10px; background:#020617; color:#fff; border:1px solid #334155; border-radius:8px;"></select>
                
                <button id="ghid-cta" style="display:none; width:100%; padding:15px; background:#f59e0b; color:#000; font-weight:bold; border-radius:8px; border:none; cursor:pointer; text-transform: uppercase;">INJECT PAYLOAD</button>
            </div>
        `;
    }

    cacheElements() {
        this.el = {
            provider: document.getElementById('ghid-provider'),
            filter: document.getElementById('ghid-filter'),
            model: document.getElementById('ghid-model'),
            cta: document.getElementById('ghid-cta'),
            status: document.getElementById('ghid-status-log')
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
            if (!res.ok) throw new Error("Manifest unreachable");
            const data = await res.json();
            
            this.el.status.innerText = "🟢 MESH ONLINE";
            this.el.status.style.color = '#10b981';
            this.el.status.style.display = 'block';
            
            let html = '<option value="">-- SELECT PROVIDER --</option>';
            data.forEach(p => html += `<option value="${p}">${p.toUpperCase()}</option>`);
            this.el.provider.innerHTML = html;
        } catch (err) {
            this.el.status.innerText = "🔴 MESH OFFLINE (Local Cache Only)";
            this.el.status.style.color = '#ef4444';
            this.el.status.style.display = 'block';
            this.el.provider.innerHTML = '<option value="">-- OFFLINE --</option>';
        }
    }

    async fetchModels(provider) {
        if (!provider) return;
        
        this.el.model.innerHTML = '<option>HYDRATING...</option>';
        this.el.filter.value = 'all';
        this.el.filter.disabled = true;
        this.el.model.disabled = true;
        this.el.cta.style.display = 'none';

        try {
            this.el.status.innerText = `📡 Handshaking with ${provider.toUpperCase()}...`;
            this.el.status.style.color = '#38bdf8';
            
            // 1. Initial hit to check if it's an aggregator
            const res = await fetch(`${this.apiEndpoint}/api/v1/manifest/${provider}?mode=standard`);
            const data = await res.json();
            this.selectedProviderType = data.type || "maker";
            
            // 2. Requirement 2: Aggregator Logic - Force Raw Mode and Live Discovery
            if (this.selectedProviderType === 'aggregator') {
                this.el.status.innerText = "🔥 Aggregator detected! Unlocking live Firehose...";
                this.el.status.style.color = '#f59e0b'; // Amber
                
                const rawRes = await fetch(`${this.apiEndpoint}/api/v1/manifest/${provider}?mode=raw`);
                const rawData = await rawRes.json();
                
                // Prioritize live pulled models, fallback to static if fetch fails
                this.models = (rawData.models && rawData.models.length > 0) ? rawData.models : data.models;
            } else {
                this.el.status.innerText = "🟢 Direct Maker detected.";
                this.el.status.style.color = '#10b981';
                this.models = data.models || [];
            }

            this.el.filter.disabled = false;
            this.el.model.disabled = false;
            this.applyFilter();

        } catch (err) {
            console.error(err);
            this.el.status.innerText = "🔴 MANIFEST ERROR";
            this.el.status.style.color = '#ef4444';
        }
    }

    applyFilter() {
        const type = this.el.filter.value;
        const filtered = this.models.filter(m => type === "all" || m.type === type);
        let html = `<option value="">-- ${filtered.length} TARGETS AVAILABLE --</option>`;
        filtered.forEach(m => html += `<option value="${m.model_id}">${m.model_id}</option>`);
        this.el.model.innerHTML = html;
        this.el.cta.style.display = 'none';
    }

    stageModel(modelId) {
        if (!modelId) return;
        const model = this.models.find(m => m.model_id === modelId);
        this.el.cta.style.display = 'block';
        this.el.cta.innerText = `INJECT ${model.type} PAYLOAD`;
    }
}
