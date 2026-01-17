import os
import time
import streamlit as st
from together import Together
from huggingface_hub import HfApi


class ModelHarvester:
    @staticmethod
    @st.cache_data(ttl=3600)  # Cache results for 1 hour
    def get_together_models():
        """
        Fetches ALL active models from Together AI.
        Robustly handles different API response versions.
        """
        api_key = os.getenv("TOGETHER_API_KEY")
        if not api_key: return []

        # Retry logic for transient 503 errors
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Fix: Ensure env var is set, then init client without explicit arg if it fails
                # Some versions of 'together' library prefer os.environ over explicit init
                os.environ["TOGETHER_API_KEY"] = api_key

                try:
                    client = Together(api_key=api_key)
                except TypeError:
                    # Fallback for versions that don't accept api_key in init
                    client = Together()

                models = client.models.list()

                clean_list = []
                for m in models:
                    # Defensive Coding: Handle both object attributes and dictionary keys
                    m_id = getattr(m, 'id', None)
                    m_type = getattr(m, 'type', None)
                    m_context = getattr(m, 'context_length', None)

                    # Fallback for dictionary access if object access fails
                    if m_id is None and isinstance(m, dict):
                        m_id = m.get('id')
                        m_type = m.get('type')
                        m_context = m.get('context_length')

                    if m_id:
                        clean_list.append({
                            "id": m_id,
                            "type": str(m_type) if m_type else "chat",  # Default to chat if unknown
                            "context": m_context
                        })
                return clean_list

            except Exception as e:
                # If it's a 503 Service Unavailable, wait and retry
                error_str = str(e).lower()
                if "503" in error_str or "service unavailable" in error_str:
                    if attempt < max_retries - 1:
                        time.sleep(2 * (attempt + 1))  # Exponential backoff: 2s, 4s, etc.
                        continue

                # Log the error to console but return empty list to prevent Dashboard Crash
                print(f"Harvester Error (Together): {e}")
                return []
        return []

    @staticmethod
    @st.cache_data(ttl=3600)
    def get_huggingface_models(limit=50):
        """
        Fetches popular text-generation models from HF Hub.
        """
        try:
            token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
            # Fallback: public access if no token (rate limited)
            api = HfApi(token=token)

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