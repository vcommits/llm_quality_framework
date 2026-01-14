*** Settings ***
Documentation     A test suite for running interactive, single-shot tests from the command line.
Library           llm_tests.LLMKeywords
Suite Setup       Log To Console    --- Initializing Interactive Test Run ---
Suite Teardown    Log To Console    --- Interactive Test Run Complete ---

*** Variables ***
# These variables are DESIGNED to be overridden from the command line.
${PROVIDER}       grok
${TIER}           lite
${MODEL}          ${None} # Allow overriding the model directly
${SYSTEM_PROMPT}  ${None}
${PROMPT}         Who was the first WNBA player to dunk in a game?
${MOCK_MODE}      ${False}
${TEST_CASE_ID}   TC-Interactive-001
${TEST_TYPE}      Ad-Hoc

# --- NEW: Control LangTest from the command line ---
${RUN_LANGTEST}   ${False}

*** Test Cases ***
Execute Ad-Hoc LLM Test
    [Documentation]    This single test case is a template for command-line execution.

    # Step 1: Run the core API test to get a response
    ${response_text}=    Run Test Against Provider And Tier
    ...    provider=${PROVIDER}
    ...    tier=${TIER}
    ...    prompt=${PROMPT}
    ...    system_prompt=${SYSTEM_PROMPT}
    ...    mock_mode=${MOCK_MODE}

    Should Not Be Empty    ${response_text}
    Log To Console    Response from ${PROVIDER.upper()} (${TIER}): ${response_text}

    # Step 2: Run DeepEval evaluations only if not in mock mode
    Run Keyword If    not ${MOCK_MODE}
    ...    Run And Save DeepEval Evaluations
    ...    ${response_text}

    # Step 3: Run LangTest evaluation only if not in mock mode AND explicitly enabled
    Run Keyword If    not ${MOCK_MODE} and ${RUN_LANGTEST}
    ...    Run Robustness Test With Langtest
    ...    test_case_id=${TEST_CASE_ID}
    ...    provider=${PROVIDER}
    ...    tier=${TIER}
    ...    prompt=${PROMPT}

*** Keywords ***
Run And Save DeepEval Evaluations
    [Arguments]    ${response_text}
    [Documentation]    A wrapper keyword to run all DeepEval evaluations and save their results.

    # --- Run DeepEval evaluations and save each result ---
    ${toxicity_result}=    Evaluate Response For Toxicity
    ...    prompt=${PROMPT}
    ...    response_text=${response_text}

    Save Evaluation Result
    ...    test_case_id=${TEST_CASE_ID}
    ...    provider=${PROVIDER}
    ...    model=${MODEL}
    ...    model_tier=${TIER}
    ...    test_type=${TEST_TYPE}
    ...    prompt=${PROMPT}
    ...    system_prompt=${SYSTEM_PROMPT}
    ...    response=${response_text}
    ...    mock_mode=${MOCK_MODE}
    ...    evaluation_result=${toxicity_result}
    ...    metric_name=Toxicity

    ${relevancy_result}=    Evaluate Response For Relevancy
    ...    prompt=${PROMPT}
    ...    response_text=${response_text}

    Save Evaluation Result
    ...    test_case_id=${TEST_CASE_ID}
    ...    provider=${PROVIDER}
    ...    model=${MODEL}
    ...    model_tier=${TIER}
    ...    test_type=${TEST_TYPE}
    ...    prompt=${PROMPT}
    ...    system_prompt=${SYSTEM_PROMPT}
    ...    response=${response_text}
    ...    mock_mode=${MOCK_MODE}
    ...    evaluation_result=${relevancy_result}
    ...    metric_name=Relevancy
