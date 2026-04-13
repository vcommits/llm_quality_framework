# ghidorah_sentry/model_data.py
# This file serves as the master static database for the curated model manifest.
# It contains the de-duplicated and unified list of all models from reconnaissance.

GHIDORAH_MASTER_MANIFEST = [
    {
        "provider": "Together AI",
        "models": [
            {
                "name": "Llama 3 70B Instruct",
                "author": "Meta",
                "category": "text",
                "type": "text",
                "context_length": 8192,
                "pricing": {"input_per_1m": 0.9, "output_per_1m": 0.9},
                "tier": "Enterprise",
                "weightclass": "Heavyweight",
                "status": "online"
            },
            {
                "name": "Mixtral 8x7B Instruct",
                "author": "Mistral AI",
                "category": "text",
                "type": "text",
                "context_length": 32768,
                "pricing": {"input_per_1m": 0.6, "output_per_1m": 0.6},
                "tier": "Production",
                "weightclass": "Midweight",
                "status": "online"
            }
        ]
    },
    {
        "provider": "Fireworks AI",
        "models": [
            {
                "name": "Llama 3 8B Instruct",
                "author": "Meta",
                "category": "text",
                "type": "text",
                "context_length": 8192,
                "pricing": {"input_per_1m": 0.2, "output_per_1m": 0.2},
                "tier": "Edge",
                "weightclass": "Lightweight",
                "status": "online"
            },
            {
                "name": "Firellava-13B",
                "author": "Fireworks",
                "category": "multimodal",
                "type": "multimodal",
                "context_length": 4096,
                "pricing": {"input_per_1m": 0.2, "output_per_1m": 0.2},
                "tier": "Experimental",
                "weightclass": "Midweight",
                "status": "online"
            }
        ]
    },
    {
        "provider": "DeepInfra",
        "models": [
            {
                "name": "Qwen2 72B Instruct",
                "author": "Alibaba",
                "category": "text",
                "type": "text",
                "context_length": 32768,
                "pricing": {"input_per_1m": 0.35, "output_per_1m": 0.35},
                "tier": "Enterprise",
                "weightclass": "Heavyweight",
                "status": "online"
            },
            {
                "name": "Phind CodeLlama 34B",
                "author": "Phind",
                "category": "text",
                "type": "text",
                "context_length": 16384,
                "pricing": {"input_per_1m": 0.6, "output_per_1m": 0.6},
                "tier": "Specialized",
                "weightclass": "Midweight",
                "status": "online"
            }
        ]
    },
    {
        "provider": "OpenRouter",
        "models": [
            {
                "name": "Claude 3.5 Sonnet",
                "author": "Anthropic",
                "category": "text",
                "type": "text",
                "context_length": 200000,
                "pricing": {"input_per_1m": 3.0, "output_per_1m": 15.0},
                "tier": "Elite",
                "weightclass": "Heavyweight",
                "status": "online"
            },
            {
                "name": "GPT-4o Mini",
                "author": "OpenAI",
                "category": "text",
                "type": "text",
                "context_length": 128000,
                "pricing": {"input_per_1m": 0.15, "output_per_1m": 0.6},
                "tier": "Production",
                "weightclass": "Lightweight",
                "status": "online"
            }
        ]
    }
]
