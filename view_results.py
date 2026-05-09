# File: view_results.py
# Purpose: A utility script to view the latest test run results from the Results directory.

import os
import json
import glob

def view_latest_results():
    """Finds the most recent JSON results file and prints a summary."""
    
    # Path to the results directory
    results_dir = os.path.join(os.path.dirname(__file__), 'Results')
    
    if not os.path.exists(results_dir):
        print(f"Error: The '{results_dir}' directory does not exist. Run some tests first.")
        return

    # Find all JSON files in the directory
    list_of_files = glob.glob(os.path.join(results_dir, '*.json'))
    
    if not list_of_files:
        print("No results files found in the 'Results' directory.")
        return

    # Find the latest file based on modification time
    latest_file = max(list_of_files, key=os.path.getmtime)
    
    print(f"--- Displaying results from: {os.path.basename(latest_file)} ---\n")

    try:
        with open(latest_file, 'r') as f:
            data = json.load(f)
            
        if not data:
            print("The results file is empty.")
            return
            
        # Print a summary of each record
        for i, record in enumerate(data):
            print(f"--- Record {i+1} ---")
            print(f"  Test Case ID: {record.get('test_case_id', 'N/A')}")
            print(f"  Provider:     {record.get('provider', 'N/A')}")
            print(f"  Model:        {record.get('model', 'N/A')}")
            print(f"  Timestamp:    {record.get('timestamp', 'N/A')}")
            
            # Pretty-print the response if it's a dictionary or list
            response = record.get('response')
            if isinstance(response, (dict, list)):
                print(f"  Response:     {json.dumps(response, indent=4)}")
            else:
                print(f"  Response:     {response}")
                
            print("-" * (len(str(i+1)) + 12)) # Dynamic separator length
            
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{latest_file}'. The file may be corrupted.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    view_latest_results()
