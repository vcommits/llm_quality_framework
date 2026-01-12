# File: explorations/langtest_spike.py
# Purpose: A minimal script to test the langtest library installation in isolation.
# This helps debug dependency issues without the complexity of the full framework.

print("--- Attempting to import and run a basic LangTest Harness ---")

try:
    # We are attempting the most basic import and harness creation.
    from langtest import Harness
    import pandas as pd

    # Set pandas display options for readable output in the terminal.
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)

    print("-> LangTest imported successfully.")

    # 1. Define a simple model and data source.
    # We'll use a free, open-source model from Hugging Face for this test.
    # The goal is just to see if the Harness object can be created without errors.
    harness = Harness(
        task="question-answering",
        model={"model": "dslim/bert-base-NER", "hub": "huggingface"},
        data={"data_source": [{"question": "Who is the CEO of Apple?", "expected_result": "Tim Cook"}]}
    )

    print("-> Harness created successfully.")

    # --- Temporarily disabling configure and run to isolate the dependency issue ---
    # We will re-enable these steps once the core import is confirmed to be working.

    # print("-> Configuration complete.")
    # print("-> Generating test cases...")
    # harness.generate()
    # print("-> Running tests...")
    # harness.run()
    # print("-> Run complete.")

    # report_df = harness.report(format="dataframe")

    print("\n✅ LangTest Spike Test Successful! (Core library loaded without errors)")
    # print("--- LangTest Results Summary ---")
    # print(report_df)
    # print("------------------------------")

except Exception as e:
    print(f"\n❌ LangTest Spike Test FAILED.")
    print(f"An error occurred: {e}")
    # The following line will print the full traceback for detailed debugging.
    import traceback

    traceback.print_exc()

