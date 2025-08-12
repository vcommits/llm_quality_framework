# File: llm_tests/db_logger.py
# Purpose: Handles all database operations for logging test results.

import sqlite3
import uuid
from datetime import datetime

DB_NAME = "llm_quality_framework.db"

def setup_database():
    """
    Sets up the database and creates the results table if it doesn't exist.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS test_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        test_run_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        provider TEXT NOT NULL,
        tier TEXT NOT NULL,
        attack_method TEXT,
        vulnerability TEXT,
        vulnerability_type TEXT,
        prompt TEXT,
        response TEXT,
        score REAL,
        reason TEXT
    )
    """)
    conn.commit()
    conn.close()

def log_results(risk_assessment, provider: str, tier: str, test_run_id: str):
    """
    Logs all test cases from a risk_assessment object to the database.

    Args:
        risk_assessment: The result object from the deepteam.red_team() call.
        provider: The name of the LLM provider (e.g., 'gemini').
        tier: The model tier used (e.g., 'lite').
        test_run_id: The unique ID for this specific test run.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    for test_case in risk_assessment.test_cases:
        # The vulnerability_type can be an Enum, so we access its .value property
        vuln_type_str = test_case.vulnerability_type.value if hasattr(test_case.vulnerability_type, 'value') else str(test_case.vulnerability_type)

        cursor.execute("""
        INSERT INTO test_results (
            test_run_id, timestamp, provider, tier, attack_method,
            vulnerability, vulnerability_type, prompt, response, score, reason
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            test_run_id,
            datetime.now().isoformat(),
            provider,
            tier,
            test_case.attack_method,
            test_case.vulnerability,
            vuln_type_str,
            test_case.input,
            test_case.actual_output,
            test_case.score,
            test_case.reason
        ))

    conn.commit()
    conn.close()
    print(f"\n[INFO] Successfully logged {len(risk_assessment.test_cases)} test cases to '{DB_NAME}' with run_id: {test_run_id}")

