// web/ModelPicker.js

document.addEventListener('DOMContentLoaded', () => {
    const providerSelect = document.getElementById('provider-select');
    const modelListDiv = document.getElementById('model-list');
    
    // The IP of your Raspberry Pi (Node 1)
    const SENTRY_HOST = 'http://192.168.8.200:8080';

    // 1. Fetch and populate the list of providers on page load
    async function populateProviders() {
        try {
            const response = await fetch(`${SENTRY_HOST}/providers`);
            if (!response.ok) throw new Error('Failed to fetch providers');
            
            const providers = await response.json();
            
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

    // 2. Fetch and display models when a provider is selected
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

            // Render the "Firehose" list
            modelListDiv.innerHTML = models.map(model => `
                <div class="p-2 border-b border-gray-700 hover:bg-gray-700 cursor-pointer">
                    <p class="font-bold">${model.name}</p>
                    <p class="text-xs text-gray-400">${model.model_id}</p>
                </div>
            `).join('');

        } catch (error) {
            modelListDiv.innerHTML = `<p class="text-red-500">Error: ${error.message}</p>`;
            console.error(error);
        }
    }

    // --- Event Listeners ---
    providerSelect.addEventListener('change', (event) => {
        fetchModelsForProvider(event.target.value);
    });

    // --- Initial Load ---
    populateProviders();
});
