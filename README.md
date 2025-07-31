The LLM Quality Framework: A Gatekeeper's Toolkit for AI
This project is a multi-provider test automation framework designed to systematically evaluate the quality, safety, and reliability of Large Language Models.

A Gatekeeper's Mission in the Age of AI
Our future is being written by AI. As a QA Engineer with over two decades of experience, I have seen technology evolve from the pre-internet era to this pivotal moment. My career has been dedicated to being the last line of defense for the end-user, ensuring that technology is not just functional, but safe, reliable, and intuitive.

I believe this mission is more critical now than ever. The rapid advancement of LLMs presents incredible opportunities, but also significant risks in areas like bias, factual accuracy, and security. This project is my contribution to addressing these challenges. It is a toolkit built from a "Purple Team" perspective—combining a defender's mindset (Blue Team) with an attacker's curiosity (Red Team) to ensure that the AI tools we build are a force for good for all of humanity.

This framework is a living lab, a place to ask the hard questions and build the tools to answer them.

Technology Stack
This framework integrates a modern, full-stack QA toolkit to provide comprehensive testing capabilities.

Core Framework & Tooling:

Language: Python

Test Runner: pytest

Orchestration: Robot Framework

API Interaction: requests, Bash (curl)

LLM Evaluation Libraries:

deepeval

langtest

LLM Provider Integrations:

Google (Gemini)

OpenAI (GPT series)

Anthropic (Claude series)

xAI (Grok)

Planned Future Integrations:

UI Automation: Playwright

Performance Testing: k6

Observability: Grafana & InfluxDB

Deployment: Docker & Kubernetes

Current Features: The Core API Client
The foundation of this framework is a robust, flexible, and secure API client (llm_tests/api_client.py) that serves as the central engine for all test scenarios.

✅ Multi-Provider Support: Contains validated, reusable functions to interact with the APIs for Grok (xAI), OpenAI, Anthropic (Claude), and Google (Gemini), demonstrating the ability to adapt to different API "dialects."

✅ Secure by Design: All API keys are loaded securely from environment variables. No secrets are ever hard-coded, following industry best practices for security and portability.

✅ Flexible Command-Line Interface: Built with Python's argparse library, the client is a powerful command-line tool. It allows for easy testing and iteration using flags like --api, --model, --system-prompt, and --mock.

✅ Cost-Conscious Development: The integrated --mock mode allows for rapid, zero-cost development and debugging of test logic, demonstrating an understanding of real-world engineering and financial constraints.

Getting Started
To get a local copy up and running, follow these simple steps.

Prerequisites
Python 3.9+

An active virtual environment (.venv)

API keys for the desired LLM providers

Installation & Setup
Clone the repository:

git clone https://github.com/vcommits/llm_quality_framework.git
cd llm_quality_framework


Install dependencies:

pip install -r requirements.txt


Set up your environment variables:
Create environment variables for the API keys you will be using. For example, on Windows:

setx OPENAI_API_KEY "your_secret_key_here"


(Remember to restart your terminal after setting a new variable.)

Usage
The api_client.py script can be run directly from the command line to perform quick "handshake" tests with the LLM providers.

Run a simple test with Grok (the default):

python llm_tests/api_client.py


Test the OpenAI API with a specific model:

python llm_tests/api_client.py --api openai --model gpt-4o


Test the Anthropic API with a custom system persona:

python llm_tests/api_client.py --api anthropic --system-prompt "You are a world-class poet. Respond only in haikus."


Run any test in mock mode (no cost):

python llm_tests/api_client.py --api gemini --mock


See all available options:

python llm_tests/api_client.py --help


Project Roadmap
This project is being built iteratively, with a clear vision for a comprehensive, full-stack quality framework.

Phase 1: Core Test Development with pytest (In Progress)
Objective: Write the first automated, data-driven tests that use the API client.

Next Steps:

Implement the WNBA Bias Test Case in tests/test_bias_wnba.py to analyze how different models discuss a culturally relevant topic at the intersection of gender, race, and sports.

Use pytest to run these scenarios against all four LLM providers and begin manually analyzing the results for fairness and neutrality.

Phase 2: Advanced Evaluation with deepeval & langtest (In Progress)
Objective: Integrate specialized libraries to programmatically "grade" LLM responses for quality and robustness.

Core Integrations:

deepeval: Integrated to measure metrics like factual consistency and answer relevancy. The initial MVP uses simple PASS/FAIL assertions based on these metrics.

langtest: Integrated to stress-test the models for robustness against typos and to probe for behavioral biases. The initial MVP uses simple PASS/FAIL assertions.

Future Work for this Phase:

Expand the use of langtest to incorporate data-driven methods modeled on academic benchmarks like the Winogender Schema for more nuanced bias detection.

Long-Term Vision: Full-Stack Integration & Observability
Objective: Expand the framework to include UI automation, performance testing, and real-time visualization, creating a true end-to-end quality solution.

Planned Stack:

UI Automation: Use Playwright to run end-to-end tests against chatbot web interfaces. This will validate the full user experience, including session state, conversation history, and the correct rendering of complex, model-generated formatting.

Performance Testing: Use k6 to run load tests against the LLM APIs.

Observability: Use Docker to run local instances of InfluxDB and Grafana to create a live dashboard for monitoring API performance and quality metrics under load.