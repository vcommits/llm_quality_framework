import json
import random
from typing import List, Dict, Any

# Define possible values for our mock models
PROVIDERS = ["Together", "Fireworks", "DeepInfra", "Gemini", "Claude", "OpenAI", "Grok", "HuggingFace", "Perplexity"]
MODEL_TYPES = ["chat", "image", "code", "embedding", "audio", "video", "rerank", "functional"]
DEPLOYMENTS = ["serverless", "dedicated", "cloud_spot"]
UNITS = ["1M tokens", "images", "minutes", "seconds"]

def generate_mock_model(provider: str) -> Dict[str, Any]:
    """Generates a single mock model entry."""
    model_type = random.choice(MODEL_TYPES)
    deployment = random.choice(DEPLOYMENTS)
    unit = random.choice(UNITS)

    # Simulate pricing
    input_cost = round(random.uniform(0.05, 20.0), 2)
    output_cost = round(random.uniform(0.05, 20.0), 2) if model_type != "embedding" else None

    # Simulate model names
    if model_type == "chat":
        name_prefix = random.choice(["Llama", "Mixtral", "GPT", "Gemma", "Qwen", "Dolphin", "Mistral"])
        name_suffix = random.choice(["8B", "70B", "1.5 Pro", "Flash", "Instruct", "Chat", "Ultra"])
        name = f"{name_prefix} {name_suffix}"
    elif model_type == "image":
        name = random.choice(["SDXL", "DALL-E 3", "Midjourney V6", "Stable Diffusion"])
    elif model_type == "code":
        name = random.choice(["CodeLlama", "DeepSeek Coder", "StarCoder"])
    elif model_type == "audio":
        name = random.choice(["Whisper Large V3", "Chirp STT", "ElevenLabs TTS"])
    else:
        name = f"{model_type.capitalize()} Model {random.randint(1, 10)}"

    model_id = f"{provider.lower().replace(' ', '-')}/{name.lower().replace(' ', '-')}-{random.randint(100, 999)}"

    return {
        "model_id": model_id,
        "name": name,
        "provider": provider,
        "type": model_type,
        "deployment": deployment,
        "pricing": {
            "input_cost": input_cost,
            "output_cost": output_cost,
            "unit": unit
        }
    }

def generate_firehose_data(num_models_per_provider: int = 20) -> Dict[str, List[Dict[str, Any]]]:
    """Generates a large dictionary of mock model data."""
    firehose_data = {}
    for provider in PROVIDERS:
        firehose_data[provider] = []
        for _ in range(num_models_per_provider):
            firehose_data[provider].append(generate_mock_model(provider))
    return firehose_data

if __name__ == "__main__":
    output_file = "manifest_firehose.json"
    num_models = 50 # Generate 50 models per provider for a truly massive list
    
    print(f"Generating {num_models * len(PROVIDERS)} mock models for the Firehose...")
    data = generate_firehose_data(num_models)
    
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Firehose data saved to {output_file}")
