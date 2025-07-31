*** Settings ***
Documentation     A test suite for running interactive, single-shot tests from the command line.
Library           llm_tests.LLMKeywords
Suite Setup       Log To Console    --- Initializing Interactive Test Run ---
Suite Teardown    Log To Console    --- Interactive Test Run Complete ---

*** Variables ***
# These variables are DESIGNED to be overridden from the command line.
${PROVIDER}       grok
${TIER}           lite
${SYSTEM_PROMPT}    ${None}
${PROMPT}         Who was the first WNBA player to dunk in a game?
${MOCK_MODE}      ${False}

# --- NEW: Control LangTest from the command line ---
# This variable can be overridden with -v LANGTEST_TYPE:security or -v LANGTEST_TYPE:fairness etc.
${LANGTEST_TYPE}  robustness


*** Test Cases ***
Execute Ad-Hoc LLM Test
    [Documentation]    This single test case is a template for command-line execution.

    Run Test For Provider And Tier    ${PROVIDER}    ${TIER}

*** Keywords ***
Run Test For Provider And Tier
    [Arguments]    ${provider_arg}    ${tier_arg}
    [Documentation]    This keyword calls the correct API and evaluates the response.

    ${response}=    Run Test Against Provider And Tier
    ...    provider=${provider_arg}
    ...    tier=${tier_arg}
    ...    prompt=${PROMPT}
    ...    system_prompt=${SYSTEM_PROMPT}
    ...    mock_mode=${MOCK_MODE}

    Should Not Be Empty    ${response}
    Log To Console    Response from ${provider_arg.upper()} (${tier_arg}): ${response}

    # --- Run DeepEval evaluations on the single response ---
    Evaluate Response For Toxicity       prompt=${PROMPT}    response_text=${response}
    Evaluate Response For Relevancy    prompt=${PROMPT}    response_text=${response}

    # --- Run LangTest evaluation on the model's behavior ---
    Run Keyword If    not ${MOCK_MODE}    Evaluate Model With Langtest
    ...    provider=${provider_arg}
    ...    tier=${tier_arg}
    ...    prompt=${PROMPT}
    ...    test_type=${LANGTEST_TYPE}

