// web/ModelPicker.js

document.addEventListener('DOMContentLoaded', () => {
    // --- UI Elements ---
    const providerSelect = document.getElementById('provider-select');
    const modelListDiv = document.getElementById('model-list');
    const modeRadios = document.querySelectorAll('input[name="selection-mode"]');
    const tierSelectionContainer = document.getElementById('tier-selection-container');
    const tierSelect = document.getElementById('tier-select');

    // --- CORRECTED Configuration ---
    // Using the Tailscale IP for Node 1 (The Sentry)
    const SENTRY_HOST = 'http://100.101.24.26:8080'; // Manifest Server
    const LIBRARIAN_HOST = 'http://100.101.24.26:8081'; // Librarian for Secrets

    // ... (The rest of the file remains the same) ...
    const TIER_OPTIONS = {
        "together": ["lite", "mid", "vision", "code", "judge"],
        "huggingface": ["judge", "lite"],
        "openrouter": ["lite", "mid", "uncensored", "judge"],
        "mistral": ["lite", "mid", "full", "code", "vision"],
        "default": ["lite", "vision", "full"]
    };
    let currentMode = 'standard';
    let currentProvider = '';

    async function populateProviders() {
        try {
            const response = await fetch(`${SENTRY_HOST}/providers`);
            if (!response.ok) throw new Error('Failed to fetch providers');
            const providers = await response.json();
            
            providerSelect.innerHTML = '<option value="">-- Select --</option>';
            providers.forEach(provider => {
                const option = document.createElement('option');
                option.value = provider;
                option.textContent = provider;
                providerSelect.appendChild(option);
            });
        } catch (error) {
            providerSelect.innerHTML = `<option value="">Error loading providers</option>`;
            console.error(error);
        }
    }

    function updateUI() {
        currentProvider = providerSelect.value;
        if (currentMode === 'standard') {
            tierSelectionContainer.style.display = 'block';
            modelListDiv.innerHTML = '<p class="text-gray-500">Select a provider and tier.</p>';
            populateTiers(currentProvider);
        } else {
            tierSelectionContainer.style.display = 'none';
            fetchModelsForProvider(currentProvider);
        }
    }

    function populateTiers(provider) {
        const options = TIER_OPTIONS[provider] || TIER_OPTIONS['default'];
        tierSelect.innerHTML = options.map(tier => `<option value="${tier}">${tier}</option>`).join('');
    }

    async function fetchModelsForProvider(provider) {
        if (!provider) {
            modelListDiv.innerHTML = '<p class="text-gray-500">Select a provider to see available models.</p>';
            return;
        }
        modelListDiv.innerHTML = '<p class="text-cyan-400 animate-pulse">Fetching models...</p>';
        try {
            const response = await fetch(`${SENTRY_HOST}/manifest/${provider}`);
            if (!response.ok) throw new Error(`Failed to fetch models for ${provider}`);
            const models = await response.json();
            
            if (models.length === 0) {
                modelListDiv.innerHTML = `<p class="text-yellow-500">No models found for ${provider}.</p>`;
                return;
            }

            modelListDiv.innerHTML = models.map(model => `
                <div class="model-item p-3 border-b border-gray-700 hover:bg-gray-700 cursor-pointer" data-model-id="${model.model_id}">
                    <p class="font-bold text-purple-400">${model.name}</p>
                    <p class="text-xs text-gray-400">${model.model_id}</p>
                    <p class="text-xs text-cyan-400">Type: ${model.type}</p>
                    <div class="secret-status mt-2 text-xs"></div>
                </div>
            `).join('');

            document.querySelectorAll('.model-item').forEach(item => {
                item.addEventListener('click', handleModelSelection);
            });

        } catch (error) {
            modelListDiv.innerHTML = `<p class="text-red-500">Error: ${error.message}</p>`;
            console.error(error);
        }
    }

    function handleModelSelection(event) {
        document.querySelectorAll('.model-item').forEach(item => {
            item.classList.remove('bg-gray-700');
            item.querySelector('.secret-status').innerHTML = '';
        });

        const selectedItem = event.currentTarget;
        selectedItem.classList.add('bg-gray-700');
        const modelId = selectedItem.dataset.modelId;
        
        const secretStatusDiv = selectedItem.querySelector('.secret-status');
        secretStatusDiv.innerHTML = `
            <button class="inject-key-btn mt-2 px-3 py-1 bg-yellow-600 text-white text-xs font-bold rounded hover:bg-yellow-500" data-model-id="${modelId}">
                Fetch Secret for ${modelId}
            </button>
        `;

        selectedItem.querySelector('.inject-key-btn').addEventListener('click', async (e) => {
            e.stopPropagation();
            const button = e.target;
            button.textContent = 'Fetching...';
            button.disabled = true;

            const mockPrompt = `This is a test prompt for model ${modelId}. #glider`;
            
            try {
                const response = await fetch(`${LIBRARIAN_HOST}/inject-identity`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: mockPrompt })
                });

                const result = await response.json();

                if (result.key_injected) {
                    button.parentElement.innerHTML = `<span class="text-green-400">✅ Secret '${result.secret_name}' Injected!</span>`;
                } else {
                     button.parentElement.innerHTML = `<span class="text-gray-500">No identity tag found in prompt.</span>`;
                }

            } catch (error) {
                button.parentElement.innerHTML = `<span class="text-red-500">Error: Librarian offline or key not found.</span>`;
                console.error("Librarian error:", error);
            }
        });
    }

    providerSelect.addEventListener('change', updateUI);
    modeRadios.forEach(radio => {
        radio.addEventListener('change', (event) => {
            currentMode = event.target.value;
            updateUI();
        });
    });

    populateProviders();
    updateUI();
});
