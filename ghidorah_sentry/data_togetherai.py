# ghidorah_sentry/data_togetherai.py
# This file serves as the master static database for Together AI model metadata.

TOGETHER_AI_DATA = {
  "text_to_text_models": [
    {
      "model_name": "GLM 5.1 FP4",
      "author": "Zai Org",
      "parameters": "435.2B",
      "pricing_serverless": "$1.40 / $4.40",
      "features": ["JSON Mode", "Tool Calling"],
      "deployment": "serverless"
    },
    {
      "model_name": "MiniMax M2.7 FP4",
      "author": "MiniMaxAI",
      "parameters": "130.4B",
      "pricing_serverless": "$0.30 / $1.20",
      "features": ["JSON Mode", "Tool Calling"],
      "deployment": "serverless"
    },
    # ... all other text models with "deployment": "serverless"
  ],
  "image_to_image_models": [
    {
      "model_name": "FLUX.1 Kontext [pro]",
      "author": "Black Forest Labs",
      "category": "image",
      "model_id": "black-forest-labs/FLUX.1-kontext-pro",
      "pricing_serverless": "$0.03 / image",
      "deployment": "serverless"
    },
    # ... all other image-to-image models with "deployment": "serverless"
  ],
  "image_to_video_models": [
    {
      "model_name": "Kling 1.6 Pro",
      "author": "kwaivgl",
      "category": "video",
      "model_id": "kwaivgl/kling-1.6-pro",
      "pricing_serverless": "$0.32 per video",
      "deployment": "serverless"
    },
    # ... all other image-to-video models with "deployment": "serverless"
  ],
  "rerank_models": [
    {
      "model_name": "Salesforce Llama Rank V1 (8B)",
      "author": "salesforce",
      "category": "rerank",
      "model_id": "salesforce/Llama-Rank-V1-8B",
      "pricing_serverless": "$0.10 / 1M tokens",
      "deployment": "serverless"
    },
    # ... all other rerank models with "deployment": "serverless"
  ],
  "text_to_audio_models": [
    {
      "model_name": "Kokoro 82M",
      "author": "Hexgrad",
      "category": "audio",
      "model_id": "hexgrad/Kokoro-82M",
      "pricing_serverless": "$10.00 / 1M characters",
      "deployment": "serverless"
    },
    # ... all other text-to-audio models with "deployment": "serverless"
  ]
}
