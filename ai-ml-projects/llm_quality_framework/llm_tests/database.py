# File: llm_tests/database.py
# Purpose: Encapsulates JSON-based storage operations for LLM responses.

import json
import logging
import os
import uuid
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default to a 'results' directory in the project root
            self.results_dir = os.path.join(os.path.dirname(__file__), '..', 'Results')
        else:
            self.results_dir = db_path
        
        # Ensure the results directory exists
        os.makedirs(self.results_dir, exist_ok=True)
        
        self.current_test_run_id = str(uuid.uuid4())
        
        # Create a specific file for this test run
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_run_file = os.path.join(self.results_dir, f"run_{timestamp_str}_{self.current_test_run_id}.json")
        
        # Initialize the file with an empty list
        self._initialize_file()
        
        logger.info(f"DatabaseManager initialized. Results file: {self.current_run_file}")

    def _initialize_file(self):
        """Initializes the JSON file for the current run."""
        with open(self.current_run_file, 'w') as f:
            json.dump([], f)

    def save_response(
        self,
        test_case_id: str,
        provider: str,
        model: str,
        model_tier: str,
        test_type: str,
        prompt: str,
        response: str, # Can be str, dict, or list now
        mock_mode: bool,
        system_prompt: str = None,
        evaluation_metric: str = None,
        evaluation_score: float = None,
        evaluation_reasoning: str = None,
        robustness_test_type: str = None,
        perturbation_count: int = None,
        pass_rate: float = None,
        **kwargs # Allow arbitrary extra data
    ):
        """Saves a single LLM response and its evaluation results to the JSON file."""
        
        entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "test_run_id": self.current_test_run_id,
            "test_case_id": test_case_id,
            "provider": provider,
            "model": model,
            "model_tier": model_tier,
            "test_type": test_type,
            "prompt": prompt,
            "system_prompt": system_prompt,
            "response": response, # JSON handles complex types naturally
            "mock_mode": mock_mode,
            "evaluation": {
                "metric": evaluation_metric,
                "score": evaluation_score,
                "reasoning": evaluation_reasoning
            },
            "robustness": {
                "test_type": robustness_test_type,
                "perturbation_count": perturbation_count,
                "pass_rate": pass_rate
            },
            "extra_data": kwargs
        }

        try:
            # Read existing data
            with open(self.current_run_file, 'r') as f:
                data = json.load(f)
            
            # Append new entry
            data.append(entry)
            
            # Write back to file
            with open(self.current_run_file, 'w') as f:
                json.dump(data, f, indent=4)
                
            logger.info(f"Saved response for test_case_id '{test_case_id}' to JSON.")
            
        except Exception as e:
            logger.error(f"Error saving response for '{test_case_id}': {e}")
