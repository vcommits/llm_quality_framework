# File: llm_tests/LLMKeywords.py
# Purpose:  Acts as a bridge, exposing our Python API client functions
#           and evaluator functions as keywords that Robot Framework can understand.

import subprocess
import shlex
import sys
import os
from robot.api.deco import keyword
from robot.api import logger
from llm_tests.api_client import call_grok_api, call_openai_api, call_anthropic_api, call_gemini_api
from llm_tests.test_evaluators import evaluate_toxicity


class LLMKeywords:
    """
    This class contains all the custom keywords for interacting with LLM APIs
    and evaluating their responses.
    """

    # =========================================================================
    # DEEPTEAM RED TEAMING KEYWORD
    # =========================================================================

    @keyword(name="Run Deepteam Red Teaming")
    def run_deepteam_red_teaming(self, api: str, tier: str, attack: str, custom_prompts_file: str = None,
                                 mock: bool = False):
        """
        Executes the deepteam test runner script with specified parameters.
        """
        logger.info("--- Starting DeepTeam Red Teaming Execution from Robot Framework ---")
        logger.info(f"API: {api}, Tier: {tier}, Attack: {attack}, Custom File: {custom_prompts_file}, Mock: {mock}")

        command = [
            sys.executable,
            "tests/run_deepteam_tests.py",
            "--api", api,
            "--tier", tier,
            "--attack", attack
        ]

        if custom_prompts_file:
            command.extend(["--custom-prompts", custom_prompts_file])
        if mock:
            command.append("--mock")

        env = os.environ.copy()
        project_root = os.path.abspath('.')
        env['PYTHONPATH'] = f"{project_root}{os.pathsep}{env.get('PYTHONPATH', '')}"

        try:
            logger.info(f"Executing command: {shlex.join(command)}")
            # By removing 'capture_output', the subprocess output will appear live in the terminal.
            process = subprocess.run(
                command,
                check=True,
                env=env
            )
            logger.info("--- DeepTeam script executed successfully. ---")
        except subprocess.CalledProcessError as e:
            logger.error("!!! DEEPTEAM SCRIPT FAILED !!!")
            logger.error(f"Exit Code: {e.returncode}")
            # stdout/stderr are not captured in this mode, so we report that.
            logger.error(f"--- STDOUT ---\n{'Not captured in live output mode.'}")
            logger.error(f"--- STDERR ---\n{'Not captured in live output mode.'}")
            raise AssertionError(f"DeepTeam script failed with exit code {e.returncode}. Check logs for details.")
        except FileNotFoundError:
            logger.error("!!! SCRIPT NOT FOUND !!!")
            logger.error(
                "Could not find 'tests/run_deepteam_tests.py'. Make sure you are running tests from the project root directory.")
            raise