# File: visualize_results.py
# Purpose: Loads test results from the SQLite database into a pandas DataFrame
#          and launches an interactive PyGWalker UI for data exploration.

import sqlite3
import pandas as pd
import pygwalker as pyg
import os

# --- Configuration ---
DB_FILE = 'llm_quality_framework.db'

def main():
    """
    Main function to connect to the DB, load data, and start the visualization.
    """
    print("--- 📊 LLM Quality Framework Results Visualizer ---")

    # 1. Verify that the database file exists before proceeding.
    if not os.path.exists(DB_FILE):
        print(f"\n[ERROR] Database file not found: '{DB_FILE}'")
        print("Please run the DeepTeam tests first to generate the database.")
        return

    try:
        # 2. Connect to the SQLite database.
        print(f"\nConnecting to database: '{DB_FILE}'...")
        con = sqlite3.connect(DB_FILE)

        # 3. Define the SQL query to select all data from the test_results table.
        query = "SELECT * FROM test_results"

        # 4. Use pandas to execute the query and load the data into a DataFrame.
        #    read_sql_query is the most direct way to get data into pandas from a DB.
        print("Loading data into pandas DataFrame...")
        df = pd.read_sql_query(query, con)

        print(f"Successfully loaded {len(df)} records.")

    except (sqlite3.Error, pd.errors.DatabaseError) as e:
        print(f"\n[ERROR] A database error occurred: {e}")
        return
    finally:
        # 5. Ensure the database connection is always closed.
        if 'con' in locals() and con:
            con.close()
            print("Database connection closed.")

    # 6. Check if the DataFrame is empty.
    if df.empty:
        print("\n[INFO] The 'test_results' table is empty. No data to visualize.")
        return

    # 7. Launch the PyGWalker UI.
    #    This will automatically open a new tab in your default web browser.
    print("\nLaunching PyGWalker interactive UI... (Check your browser)")
    # The `dark='dark'` setting provides a better viewing experience.
    pyg.walk(df, dark='dark')

if __name__ == "__main__":
    main()