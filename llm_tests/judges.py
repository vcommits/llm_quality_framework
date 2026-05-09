# File: llm_tests/judges.py
import os
from deepeval.models.base_model import DeepEvalBaseLLM
from langchain_huggingface import HuggingFaceEndpoint
from langchain_openai import ChatOpenAI

# --- 1. SPECIALIZED JUDGE WRAPPERS ---

class GliderJudge(DeepEvalBaseLLM):
    def __init__(self):
        self.model = HuggingFaceEndpoint(
            repo_id="PatronusAI/glider",
            task="text-generation",
            max_new_tokens=512,
            temperature=0.1,
            huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN")
        )
    def load_model(self): return self.model
    def generate(self, prompt: str) -> str: return self.model.invoke(prompt)
    async def a_generate(self, prompt: str) -> str: return await self.model.ainvoke(prompt)
    def get_model_name(self): return "Glider (3.8B)"

class MinistralJudge(DeepEvalBaseLLM):
    def __init__(self):
        # Using ChatOpenAI as a unified client for Together to avoid langchain_together issues
        self.model = ChatOpenAI(
            model="mistralai/Ministral-8B-Instruct-2410",
            api_key=os.getenv("TOGETHER_API_KEY"),
            base_url="https://api.together.xyz/v1",
        )
    def load_model(self): return self.model
    def generate(self, prompt: str) -> str: return self.model.invoke(prompt).content
    async def a_generate(self, prompt: str) -> str: return await self.model.ainvoke(prompt).content
    def get_model_name(self): return "Ministral 8B"

class GPT4Judge(DeepEvalBaseLLM):
    def __init__(self):
        self.model = ChatOpenAI(model="gpt-4o", openai_api_key=os.getenv("OPENAI_API_KEY"))
    def load_model(self): return self.model
    def generate(self, prompt: str) -> str: return self.model.invoke(prompt).content
    async def a_generate(self, prompt: str) -> str: return await self.model.ainvoke(prompt).content
    def get_model_name(self): return "GPT-4o"

# --- 2. THE JUDGE FACTORY ---

class JudgeFactory:
    @staticmethod
    def get_judge(name: str):
        name = name.lower()
        if "glider" in name: return GliderJudge()
        if "mistral" in name or "ministral" in name: return MinistralJudge()
        if "gpt" in name: return GPT4Judge()
        raise ValueError(f"Unknown judge: {name}")