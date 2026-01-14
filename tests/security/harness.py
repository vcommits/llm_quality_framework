# File: tests/security/harness.py
import sys
import os
from langchain_core.messages import HumanMessage
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from llm_tests.providers import ProviderFactory

def probing_point(prompt_text: str) -> str:
    """Entry point for Red Team scanners (Garak/PyRIT)."""
    try:
        # Use a cheap/fast model for mass scanning
        provider = ProviderFactory.get_provider('together', 'lite')
        llm = provider.get_model()
        return llm.invoke([HumanMessage(content=prompt_text)]).content
    except Exception as e:
        return f"ERROR: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 1: print(probing_point(sys.argv[1]))