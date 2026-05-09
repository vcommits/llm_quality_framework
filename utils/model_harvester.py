import os
import time
import requests
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
                        # Standardize the type string for UI consistency
                        t_str = str(m_type).lower() if m_type else "chat"
                        if t_str == "chat": t_str = "language/chat"
                        
                        clean_list.append({
                            "id": m_id,
                            "type": t_str,
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
    def get_huggingface_models(limit=200):
        """
        Fetches popular text-generation models from HF Hub and infers specialized types via tags/naming.
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
            
            clean_list = []
            for m in models:
                m_id = m.modelId
                m_id_lower = m_id.lower()
                tags = [t.lower() for t in m.tags] if getattr(m, 'tags', None) else []
                
                # Heuristic Classification based on HF conventions
                m_type = "language/chat"
                if any(k in m_id_lower or k in tags for k in ['code', 'coder', 'starcoder', 'phind']):
                    m_type = "code"
                elif any(k in m_id_lower or k in tags for k in ['uncensored', 'dolphin', 'abliterated']):
                    m_type = "uncensored (unconstitutional)"
                elif any(k in m_id_lower or k in tags for k in ['roleplay', 'samantha', 'mytho', 'fimbulvetr', 'bagel', 'erotic']):
                    m_type = "erp / companion ai"
                elif any(k in m_id_lower or k in tags for k in ['vision', 'multimodal', 'llava']):
                    m_type = "multimodal (image/video)"

                clean_list.append({"id": m_id, "type": m_type})
            return clean_list
        except Exception as e:
            print(f"Harvester Error (HF): {e}")
            return []
            
    @staticmethod
    @st.cache_data(ttl=3600)
    def get_huggingface_collection(collection_slug):
        """
        Fetches models directly from a curated Hugging Face Collection via REST API.
        """
        try:
            # Extract just the slug if the user pasted the full URL
            slug = collection_slug.split("collections/")[-1] if "collections/" in collection_slug else collection_slug
            slug = slug.strip("/")
            
            url = f"https://huggingface.co/api/collections/{slug}"
            
            # Use token if available for private collections
            headers = {}
            token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
            if token:
                headers["Authorization"] = f"Bearer {token}"
                
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                
                clean_list = []
                for item in items:
                    item_type = item.get("type") or item.get("item_type")
                    if item_type == "model":
                        m_id = item.get("id") or item.get("item_id")
                        if m_id:
                            clean_list.append({
                                "id": m_id,
                                "type": "uncensored / roleplay (Collection)"
                            })
                return sorted(clean_list, key=lambda x: x["id"])
            else:
                print(f"Harvester Error (HF Collection HTTP): {response.status_code} - {response.text}")
                return []
        except Exception as e:
            print(f"Harvester Error (HF Collection Exception): {e}")
            return []

    @staticmethod
    @st.cache_data(ttl=3600)
    def get_openrouter_models():
        """
        Fetches the active model catalog from OpenRouter via REST API and infers types.
        """
        try:
            url = "https://openrouter.ai/api/v1/models"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                models = data.get("data", [])
                
                clean_list = []
                for m in models:
                    m_id = m.get("id", "")
                    m_id_lower = m_id.lower()
                    m_name = m.get("name", "").lower()
                    
                    # Heuristic Classification
                    m_type = "language/chat"
                    
                    # Some endpoints support multimodal/vision
                    if any(k in m_id_lower or k in m_name for k in ['vision', 'llava', 'vl', 'pixtral', 'qwen-vl']):
                        m_type = "multimodal (image/video)"
                    elif any(k in m_id_lower or k in m_name for k in ['coder', 'code', 'phind']):
                        m_type = "code"
                    elif any(k in m_id_lower or k in m_name for k in ['dolphin', 'uncensored', 'wizard', 'abliterated', 'rogue', 'evil']):
                        m_type = "uncensored (unconstitutional)"
                    elif any(k in m_id_lower or k in m_name for k in ['samantha', 'mythomax', 'roleplay', 'weaver', 'fimbulvetr', 'bagel', 'midnight', 'psyfighter', 'nitro']):
                        m_type = "erp / companion ai"
                    elif 'moderation' in m_id_lower or 'guard' in m_id_lower:
                        m_type = "moderation/guardrail"
                        
                    clean_list.append({
                        "id": m_id,
                        "type": m_type,
                        "context": m.get("context_length", 0),
                        "name": m.get("name", "")
                    })
                # Sort alphabetically by ID for easier reading
                return sorted(clean_list, key=lambda x: x["id"])
            else:
                print(f"Harvester Error (OpenRouter HTTP): {response.status_code}")
                return []
        except Exception as e:
            print(f"Harvester Error (OpenRouter Exception): {e}")
            return []

    @staticmethod
    @st.cache_data(ttl=3600)
    def get_mistral_models():
        """
        Fetches the active model catalog from Mistral API.
        """
        try:
            api_key = os.getenv("mistral_api_key") or os.getenv("MISTRAL_API_KEY")
            if not api_key: return []
            
            url = "https://api.mistral.ai/v1/models"
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                models = data.get("data", [])
                
                clean_list = []
                for m in models:
                    m_id = m.get("id", "")
                    m_type = "language/chat"
                    
                    if "vision" in m_id.lower() or "pixtral" in m_id.lower():
                        m_type = "multimodal (image/video)"
                    elif "codestral" in m_id.lower():
                        m_type = "code"
                    elif "embed" in m_id.lower() or "moderation" in m_id.lower():
                        continue # Skip embedding and moderation models from chat interface
                        
                    clean_list.append({
                        "id": m_id,
                        "type": m_type,
                        "context": m.get("max_context_length", 32768)
                    })
                return sorted(clean_list, key=lambda x: x["id"])
            else:
                print(f"Harvester Error (Mistral HTTP): {response.status_code}")
                return []
        except Exception as e:
            print(f"Harvester Error (Mistral): {e}")
            return []
