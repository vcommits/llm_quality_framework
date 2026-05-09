from deepeval.models.base_model import DeepEvalBaseLLM
from llm_tests.providers import ProviderFactory

class GliderJudge(DeepEvalBaseLLM):
    def __init__(self):
        # We target the 'judge' tier of our new 'huggingface' provider
        self.provider = ProviderFactory.get_provider("huggingface", "judge")
        self.model = self.provider.get_model()

    def load_model(self):
        return self.model

    def generate(self, prompt: str) -> str:
        # Glider is chat-based, so we invoke it standardly
        return self.model.invoke(prompt)

    async def a_generate(self, prompt: str) -> str:
        return await self.model.ainvoke(prompt)

    def get_model_name(self):
        return "PatronusAI/glider (3.8B)"