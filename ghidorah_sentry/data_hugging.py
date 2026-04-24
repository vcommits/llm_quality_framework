# ghidorah_sentry/data_hugging.py
# This file serves as the master static database for Hugging Face model metadata.

HUGGINGFACE_DATA = {
    "text_generation_models": [
        {
          "model_id": "zai-org/GLM-5.1",
          "parameters": "754B",
          "updated": "1 day ago",
          "downloads": "35.9k",
          "likes": 1120,
          "deployment": "serverless"
        },
        # ... all other text generation models with "deployment": "serverless"
    ],
    "image_to_text_models": [
        {
          "model_id": "zai-org/GLM-OCR",
          "parameters": None,
          "updated_at": "Mar 11, 2026",
          "downloads": "6.39M",
          "likes": 1600,
          "deployment": "serverless"
        },
        # ... all other image-to-text models with "deployment": "serverless"
    ],
    "audio_to_text_models": [
        {
          "model_id": "mistralai/Voxtral-Small-24B-2507",
          "parameters": "24B",
          "updated_at": "Dec 20, 2025",
          "downloads": "29.7k",
          "likes": 481,
          "deployment": "serverless"
        },
        # ... all other audio-to-text models with "deployment": "serverless"
    ],
    "image_classification_models": [
        {
          "model_id": "Falconsai/nsfw_image_detection",
          "updated_at": "Apr 6, 2025",
          "downloads": "37.9M",
          "likes": "1.05k",
          "deployment": "serverless"
        },
        # ... all other image classification models with "deployment": "serverless"
    ],
    "text_to_image_models": [
        {
          "model_id": "kpsss34/FHDR_Uncensored",
          "parameters": "12B",
          "updated_at": "Feb 26, 2026",
          "downloads": "247k",
          "likes": 384,
          "deployment": "serverless"
        },
        # ... all other text-to-image models with "deployment": "serverless"
    ],
    "image_to_video_models": [
        {
          "model_id": "Lightricks/LTX-2.3",
          "updated_at": "about 3 hours ago",
          "downloads": "1.66M",
          "likes": 945,
          "deployment": "serverless"
        },
        # ... all other image-to-video models with "deployment": "serverless"
    ],
    "zero_shot_image_classification_models": [
        {
          "model_id": "openai/clip-vit-base-patch32",
          "parameters": None,
          "updated_at": "Feb 29, 2024",
          "downloads": "20.7M",
          "likes": 909,
          "deployment": "serverless"
        },
        # ... all other zero-shot models with "deployment": "serverless"
    ],
    "text_to_speech_models": [
        {
          "model_id": "openbmb/VoxCPM2",
          "updated_at": "5 days ago",
          "downloads": "9.3k",
          "likes": 804,
          "deployment": "serverless"
        },
        # ... all other text-to-speech models with "deployment": "serverless"
    ],
    "audio_classification_models": [
        {
          "model_id": "laion/clap-htsat-fused",
          "parameters": "0.2B",
          "updated_at": "Jan 11, 2026",
          "downloads": "19M",
          "likes": 77,
          "deployment": "serverless"
        },
        # ... all other audio classification models with "deployment": "serverless"
    ]
}
