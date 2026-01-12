# File: explorations/setup_database.py
# Purpose: To create and initialize the SQLite database for storing LLM test results.
# This script should only be run once to set up the initial database file and table.

import sqlite3
import os

# Define the name of the database file.
# It will be created in the root directory of the project.
DB_FILE = "llm_responses.db"


def create_database():
    """Connects to the SQLite database file and creates the 'responses' table if it doesn't exist."""

    # Check if the database file already exists to avoid overwriting.
    if os.path.exists(DB_FILE):
        print(
            f"Database file '{DB_FILE}' already exists. To apply changes, please delete the old file and run this script again.")
        return

    print(f"Creating new database file: {DB_FILE}")

    try:
        # sqlite3.connect() will create the file if it doesn't exist.
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # --- Define the table structure using SQL ---
        # This is the blueprint for how we will store our data.
        # TEXT type is used for strings, INTEGER for numbers, and REAL for decimals.
        # PRIMARY KEY AUTOINCREMENT means each new row gets a unique, increasing ID number.
        cursor.execute('''
            CREATE TABLE responses (
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

        # Commit the changes to the database to save the new table.
        conn.commit()
        print("Table 'responses' created successfully with new columns for advanced evaluation and model tier.")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        # Always close the connection when you're done.
        if conn:
            conn.close()
            print("Database connection closed.")


# This block makes the script runnable from the command line.
if __name__ == "__main__":
    create_database()

