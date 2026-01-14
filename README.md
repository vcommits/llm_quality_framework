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

## Command-Line Usage

The `llm_tests/api_client.py` script is a powerful command-line tool for interacting directly with the supported LLM providers. All commands should be run from the root directory of the project (`.../llm_quality_framework`).

### Core Command Structure

The basic structure of the command is:

```bash
python llm_tests/api_client.py [FLAGS]
```

### Available Flags

You can combine these flags to control the behavior of the script.

| Flag | Description | Values | Default |
| :--- | :--- | :--- | :--- |
| `--api` | Selects the LLM provider to test. | `grok`, `openai`, `anthropic`, `gemini`, `all` | `grok` |
| `--tier` | Selects the model tier (a predefined level of model capability and cost). | `lite`, `mid`, `full` | `lite` |
| `--model` | Overrides the tier selection with a specific model ID. | e.g., `grok-4`, `gpt-4o`, `claude-3-opus-20240229` | `None` |
| `--prompt` | The main question or instruction to send to the LLM. | Any string. Enclose in quotes if it contains spaces. | `"Explain what a unit test is in one sentence."` |
| `--system-prompt` | Sets a custom persona or instruction for the AI to follow. | Any string. Enclose in quotes if it contains spaces. | `None` |
| `--mock` | Runs the script in "mock mode" to return a fake response without making a real API call. | N/A (flag presence enables it) | `False` |
| `--help` | Displays a helpful menu that lists all available flags and their descriptions. | N/A | N/A |

### Example Commands

Here are some copy-pasteable examples for common scenarios.

**1. Basic Handshake Tests**

These examples use default settings for a quick, low-cost test.

*   **Test Grok (default API, lite tier):**
    ```bash
    python llm_tests/api_client.py
    ```
*   **Test OpenAI (lite tier):**
    ```bash
    python llm_tests/api_client.py --api openai
    ```
*   **Test all providers (lite tier):**
    ```bash
    python llm_tests/api_client.py --api all
    ```

**2. Using Different Model Tiers**

Test different levels of model capability.

*   **Test Anthropic's mid-tier model:**
    ```bash
    python llm_tests/api_client.py --api anthropic --tier mid
    ```
*   **Test all providers using their most powerful "full" tier models:**
    ```bash
    python llm_tests/api_client.py --api all --tier full
    ```

**3. Specifying a Model ID**

Override tiers to use a specific model version.

*   **Test with OpenAI's `gpt-4o`:**
    ```bash
    python llm_tests/api_client.py --api openai --model gpt-4o
    ```
*   **Test with Anthropic's `claude-3-opus-20240229`:**
    ```bash
    python llm_tests/api_client.py --api anthropic --model claude-3-opus-20240229
    ```

**4. Sending Custom Prompts**

Provide your own questions and system instructions.

*   **Send a custom prompt to Gemini:**
    ```bash
    python llm_tests/api_client.py --api gemini --prompt "What are the key differences between Python lists and tuples?"
    ```
*   **Use a system prompt to define a persona:**
    ```bash
    python llm_tests/api_client.py --api openai --system-prompt "You are a helpful assistant who speaks like a pirate." --prompt "How do I set up a Python virtual environment?"
    ```

**5. Mock Mode for Development**

Run tests without making real (and costly) API calls.

*   **Run a mock test for any API:**
    ```bash
    python llm_tests/api_client.py --api gemini --mock --prompt "This is just a test."
    ```

**6. Getting Help**

*   **See all available options from the command line:**
    ```bash
    python llm_tests/api_client.py --help
    ```


## Project Roadmap
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