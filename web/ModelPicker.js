// web/ModelPicker.js

document.addEventListener('DOMContentLoaded', () => {
    // --- UI Elements ---
    const providerSelect = document.getElementById('provider-select');
    const modelListDiv = document.getElementById('model-list');
    const modeRadios = document.querySelectorAll('input[name="selection-mode"]');
    const standardTierRadio = document.querySelector('input[value="standard"]');
    const rawCatalogRadio = document.querySelector('input[value="raw"]');
    const tierSelectionContainer = document.getElementById('tier-selection-container');
    const tierSelect = document.getElementById('tier-select');

    // --- Configuration (Absolute URLs for the Mesh) ---
    const SENTRY_HOST = 'http://100.101.24.26:8080'; // Manifest Server

    // --- State ---
    let providersData = []; // Will store the full provider metadata
    let currentMode = 'standard';

    // --- Core Logic ---

    async function populateProviders() {
        providerSelect.innerHTML = '<option value="">📡 Contacting Sentry...</option>';
        try {
            const response = await fetch(`${SENTRY_HOST}/api/v1/providers`);
            if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to fetch providers`);
            
            providersData = await response.json(); // Store the metadata
            
            providerSelect.innerHTML = '<option value="">-- Select Provider --</option>';
            providersData.forEach(provider => {
                const option = document.createElement('option');
                option.value = provider.id;
                option.textContent = provider.name;
                providerSelect.appendChild(option);
            });
        } catch (error) {
            providerSelect.innerHTML = `<option value="">❌ Sentry Offline</option>`;
            console.error("[Mesh Error] Failed to reach Manifest Server:", error);
        }
    }

    function handleProviderChange() {
        const selectedProviderId = providerSelect.value;
        if (!selectedProviderId) {
            resetUI();
            return;
        }

        const providerMeta = providersData.find(p => p.id === selectedProviderId);
        if (!providerMeta) return;

        // Requirement 2: Conditional UI Logic for Aggregators vs Makers
        if (providerMeta.type === 'aggregator') {
            standardTierRadio.disabled = true;
            standardTierRadio.parentElement.classList.add('opacity-50', 'cursor-not-allowed');
            rawCatalogRadio.checked = true; // Force Raw Catalog mode
            currentMode = 'raw';
        } else { // It's a 'maker'
            standardTierRadio.disabled = false;
            standardTierRadio.parentElement.classList.remove('opacity-50', 'cursor-not-allowed');
            // Keep currentMode as selected by user, default to 'standard' if needed
            if (!document.querySelector('input[name="selection-mode"]:checked')) {
                standardTierRadio.checked = true;
                currentMode = 'standard';
            }
        }
        
        updateUI();
    }

    function updateUI() {
        const selectedProviderId = providerSelect.value;
        currentMode = document.querySelector('input[name="selection-mode"]:checked').value;

        if (currentMode === 'standard') {
            tierSelectionContainer.style.display = 'block';
            // In a real app, selecting a tier would trigger a fetch.
            // For now, we just show the tiers and clear the model list.
            modelListDiv.innerHTML = '<p class="text-gray-500">Select a tier to see standard models.</p>';
        } else { // Raw mode
            tierSelectionContainer.style.display = 'none';
            fetchModelsWithLiveDiscovery(selectedProviderId, 'raw');
        }
    }
    
    function resetUI() {
        standardTierRadio.disabled = false;
        standardTierRadio.parentElement.classList.remove('opacity-50', 'cursor-not-allowed');
        modelListDiv.innerHTML = '<p class="text-gray-500">Select a provider.</p>';
    }

    async function fetchModelsWithLiveDiscovery(providerId, mode) {
        if (!providerId) return;
        
        modelListDiv.innerHTML = '<p class="text-cyan-400 animate-pulse">📡 Fetching live models from Tailscale node...</p>';
        
        try {
            const url = `${SENTRY_HOST}/api/v1/models/${providerId}?mode=${mode}`;
            const response = await fetch(url);
            if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to fetch models`);
            
            const data = await response.json();
            const models = data.models || [];
            
            if (models.length === 0) {
                modelListDiv.innerHTML = `<p class="text-yellow-500">No models returned for ${providerId} in '${mode}' mode.</p>`;
                return;
            }

            modelListDiv.innerHTML = models.map(model => `
                <div class="model-item p-3 border-b border-gray-700 hover:bg-gray-700 cursor-pointer" data-model-id="${model.model_id}">
                    <p class="font-bold text-purple-400">${model.name}</p>
                    <p class="text-xs text-gray-400">${model.model_id}</p>
                    <p class="text-xs text-cyan-400">Type: ${model.type || 'chat'}</p>
                </div>
            `).join('');

        } catch (error) {
            modelListDiv.innerHTML = `
                <div class="p-4 bg-red-900/30 border border-red-500 rounded">
                    <p class="text-red-400 font-bold">Mesh Link Failure</p>
                    <p class="text-xs text-red-300">Unable to reach Sentry node. The Pi might be rebooting.</p>
                    <p class="text-xs text-gray-500 mt-2">${error.message}</p>
                </div>
            `;
            console.error("[Mesh Error] Live discovery fetch failed:", error);
        }
    }

    // --- Event Listeners ---
    providerSelect.addEventListener('change', handleProviderChange);
    modeRadios.forEach(radio => {
        radio.addEventListener('change', updateUI);
    });

    // --- Initial Load ---
    populateProviders();
});
