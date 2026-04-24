document.addEventListener("DOMContentLoaded", () => {
    // --- UI Elements (CORRECTED to match picker_test.html) ---
    const providerSelect = document.getElementById('provider-select');
    const modelSelect = document.getElementById('model-select'); // This is now a <select>
    const modeRadios = document.querySelectorAll('input[name="selection-mode"]');
    const tierSelectionContainer = document.getElementById('tier-selection-container');

    // --- Configuration ---
    const SENTRY_HOST = 'http://100.101.24.26:8080';

    // --- State ---
    let currentMode = 'standard';

    // --- Core Logic ---

    async function populateProviders() {
        providerSelect.innerHTML = '<option value="">📡 Contacting Sentry...</option>';
        try {
            const response = await fetch(`${SENTRY_HOST}/api/v1/providers`);
            if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to fetch providers`);
            
            const providers = await response.json(); 
            
            providerSelect.innerHTML = '<option value="">-- Select Provider --</option>';
            providers.forEach(providerName => {
                const option = document.createElement('option');
                option.value = providerName;
                option.textContent = providerName.charAt(0).toUpperCase() + providerName.slice(1);
                providerSelect.appendChild(option);
            });
        } catch (error) {
            providerSelect.innerHTML = `<option value="">❌ Sentry Offline</option>`;
            console.error("[Mesh Error] Failed to reach Manifest Server:", error);
        }
    }

    function updateUI() {
        const selectedProviderId = providerSelect.value;
        currentMode = document.querySelector('input[name="selection-mode"]:checked').value;

        tierSelectionContainer.style.display = 'none'; // Hide tier selection for now
        fetchModelsForProvider(selectedProviderId);
    }

    async function fetchModelsForProvider(providerId) {
        if (!providerId) {
            modelSelect.innerHTML = '<option class="text-gray-500" disabled>Select a provider.</option>';
            return;
        }
        
        modelSelect.innerHTML = '<option class="text-cyan-400" disabled>📡 Fetching models from Firehose...</option>';
        
        try {
            const url = `${SENTRY_HOST}/api/v1/manifest/${providerId}`;
            const response = await fetch(url);
            if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to fetch models`);
            
            const data = await response.json();
            const models = data.models || [];
            
            if (models.length === 0) {
                modelSelect.innerHTML = `<option class="text-yellow-500" disabled>No models returned for ${providerId}.</option>`;
                return;
            }

            // Populate the <select> dropdown
            modelSelect.innerHTML = ''; // Clear previous options
            models.forEach(model => {
                const option = document.createElement('option');
                option.value = model.model_id;
                option.textContent = model.name;
                modelSelect.appendChild(option);
            });

        } catch (error) {
            modelSelect.innerHTML = `<option class="text-red-500" disabled>Mesh Link Failure</option>`;
            console.error("[Mesh Error] Live discovery fetch failed:", error);
        }
    }

    // --- Event Listeners ---
    providerSelect.addEventListener('change', updateUI);
    modeRadios.forEach(radio => {
        radio.addEventListener('change', updateUI);
    });

    // --- Initial Load ---
    populateProviders();
});
