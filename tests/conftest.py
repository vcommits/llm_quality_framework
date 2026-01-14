# File: tests/conftest.py
import pytest
import os
import sys
# Updated imports for Phoenix/OpenInference
from phoenix.otel import register
from openinference.instrumentation.langchain import LangChainInstrumentor

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from llm_tests.providers import ProviderFactory

def pytest_addoption(parser):
    parser.addoption("--mock", action="store_true", help="Run in mock mode")
    parser.addoption("--tier", action="store", default="lite", help="Model tier")
    parser.addoption("--provider", action="store", default="together", help="Provider")
    parser.addoption("--role", action="store", default="general", help="System Role")

@pytest.fixture(scope="session")
def config(request):
    return {
        "mock": request.config.getoption("--mock"),
        "tier": request.config.getoption("--tier"),
        "provider": request.config.getoption("--provider"),
        "role": request.config.getoption("--role"),
    }

@pytest.fixture(scope="session", autouse=True)
def setup_arize_phoenix():
    print("\n🚀 Starting Arize Phoenix Tracing...")
    # Updated instrumentation logic
    tracer_provider = register()
    LangChainInstrumentor().instrument(tracer_provider=tracer_provider)
    yield

@pytest.fixture
def llm(config):
    if config["mock"]:
        class MockLLM:
            def invoke(self, messages): return type('obj', (object,), {'content': "MOCK_RESPONSE"})
        return MockLLM()
    return ProviderFactory.get_provider(config["provider"], config["tier"]).get_model()

@pytest.fixture
def system_prompt(config):
    roles = {
        "general": "You are a helpful AI assistant.",
        "wnba_analyst": "You are a WNBA data analyst. Focus on advanced stats.",
        "cap_expert": "You are a CBA expert. Be precise with financial rules."
    }
    return roles.get(config["role"], roles["general"])
