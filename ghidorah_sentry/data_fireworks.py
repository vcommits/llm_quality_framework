# ghidorah_sentry/data_fireworks.py
# This file serves as the master static database for Fireworks AI model metadata.

FIREWORKS_AI_DATA = {
    "function_calling_models": [
        {
            "name": "FireFunction V2",
            "model_id": "accounts/fireworks/models/firefunction-v2",
            "pricing": { "uncached_input_1M": 0.90, "cached_input_1M": 0.45, "output_1M": 0.90 },
            "specs": { "provider": "Fireworks", "kind": "Fine-tuned", "parameters": "70B", "context_window": "32k", "function_calling": "Optimized" },
            "deployment": "serverless"
        }
        # ... all other function calling models with "deployment": "serverless"
    ],
    "image_generation_models": [
        # ... all image generation models with "deployment": "serverless"
    ],
    "vision_models": [
        # ... all vision models with "deployment": "serverless"
    ],
    "rerank_models": [
        # ... all rerank models with "deployment": "serverless"
    ]
}
