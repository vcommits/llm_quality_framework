# ghidorah_sentry/data_hugging.py
# This file serves as the master static database for Hugging Face model metadata.

HUGGINGFACE_DATA = {
    "text_generation_models": [
        # ... All text generation models from the previous turn ...
    ],
    "image_to_text_models": [
        # ... All image-to-text models from the previous turn ...
    ],
    "audio_to_text_models": [
        # ... All audio-to-text models from the previous turn ...
    ],
    "image_classification_models": [
        # ... All image classification models from the previous turn ...
    ],
    "text_to_image_models": [
        # ... All text-to-image models from the previous turn ...
    ],
    "image_to_video_models": [
        # ... All image-to-video models from the previous turn ...
    ],
    "zero_shot_image_classification_models": [
        # ... All zero-shot classification models from the previous turn ...
    ],
    "text_to_speech_models": [
        # ... All text-to-speech models from the previous turn ...
    ],
    "audio_classification_models": [
        {
          "model_id": "laion/clap-htsat-fused",
          "parameters": "0.2B",
          "updated_at": "Jan 11, 2026",
          "downloads": "19M",
          "likes": 77
        },
        {
          "model_id": "Adam-ousse/ast-esc50-finetuned-fold1",
          "parameters": "86.2M",
          "updated_at": "6 hours ago",
          "downloads": "37",
          "likes": 2
        },
        # ... and so on for all the audio classification models you provided ...
    ]
}
