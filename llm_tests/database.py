# File: llm_tests/database.py
# Purpose: Encapsulates SQLite database operations.

import sqlite3
import logging
import os
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = None):
        if db_path is None:
            self.db_path = os.path.join(os.path.dirname(__file__), '..', 'llm_responses.db')
        else:
            self.db_path = db_path
        
        self._initialize_db()
        self.current_test_run_id = str(uuid.uuid4())
        logger.info(f"DatabaseManager initialized. Run ID: {self.current_test_run_id}")

    def _initialize_db(self):
        """Initializes the SQLite database and creates the responses table if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                test_run_id TEXT NOT NULL,
                test_case_id TEXT NOT NULL,
                provider TEXT NOT NULL,
                model TEXT NOT NULL,
                model_tier TEXT,
                test_type TEXT NOT NULL,
                prompt TEXT NOT NULL,
                system_prompt TEXT,
                response TEXT NOT NULL,
                mock_mode BOOLEAN NOT NULL,

                -- NEW COLUMNS FOR ADVANCED EVALUATION (DEEPEVAL)
                evaluation_metric TEXT,
                evaluation_score REAL,
                evaluation_reasoning TEXT,

                -- NEW COLUMNS FOR ROBUSTNESS TESTING (LANGTEST)
                robustness_test_type TEXT,
                perturbation_count INTEGER,
                pass_rate REAL
            )
        ''')
        conn.commit()
        conn.close()

    def save_response(
        self,
        test_case_id: str,
        provider: str,
        model: str,
        model_tier: str,
        test_type: str,
        prompt: str,
        response: str,
        mock_mode: bool,
        system_prompt: str = None,
        evaluation_metric: str = None,
        evaluation_score: float = None,
        evaluation_reasoning: str = None,
        robustness_test_type: str = None,
        perturbation_count: int = None,
        pass_rate: float = None
    ):
        """Saves a single LLM response and its evaluation results to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO responses (
                    test_run_id, test_case_id, provider, model, model_tier, test_type,
                    prompt, system_prompt, response, mock_mode,
                    evaluation_metric, evaluation_score, evaluation_reasoning,
                    robustness_test_type, perturbation_count, pass_rate
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.current_test_run_id, test_case_id, provider, model, model_tier, test_type,
                prompt, system_prompt, response, mock_mode,
                evaluation_metric, evaluation_score, evaluation_reasoning,
                robustness_test_type, perturbation_count, pass_rate
            ))
            conn.commit()
            logger.info(f"Saved response for test_case_id '{test_case_id}' to DB.")
        except sqlite3.Error as e:
            logger.error(f"Database error saving response for '{test_case_id}': {e}")
        finally:
            conn.close()
