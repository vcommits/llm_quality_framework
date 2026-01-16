import os
import streamlit as st
from together import Together
from huggingface_hub import HfApi

class ModelHarvester:
    @staticmethod
    @st.cache_data(ttl=3600)  # Cache results for 1 hour to prevent API rate limits
    def get_together_models():
        """
        Fetches ALL active models from Together AI.
        """
        api_key = os.getenv("TOGETHER_API_KEY")
        if not api_key: return []

        try:
            client = Together(api_key=api_key)
            models = client.models.list()
            # We return a list of dictionaries with helpful metadata
            return [
                {
                    "id": m.id,
                    "type": m.type,  # 'chat', 'image', 'language'
                    "context": m.context_length
                }
                for m in models
            ]
        except Exception as e:
            print(f"Harvester Error (Together): {e}")
            return []

    @staticmethod
    @st.cache_data(ttl=3600)
    def get_huggingface_models(limit=50):
        """
        Fetches popular text-generation models from HF Hub.
        """
        try:
            api = HfApi(token=os.getenv("HUGGINGFACEHUB_API_TOKEN"))
            models = api.list_models(
                filter="text-generation",
                sort="downloads",
                direction=-1,
                limit=limit
            )
            return [{"id": m.modelId, "type": "chat"} for m in models]
        except Exception as e:
            print(f"Harvester Error (HF): {e}")
            return []