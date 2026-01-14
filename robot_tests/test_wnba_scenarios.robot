*** Settings ***
Documentation     A data-driven test suite for evaluating LLM responses to WNBA-related prompts.
Library           llm_tests.LLMKeywords
Variables         ../config/wnba_prompts.yaml
Suite Setup       Log To Console    --- Preparing the WNBA Test Suite ---
Suite Teardown    Log To Console    --- Cleaning Up the WNBA Test Suite ---
Test Template     Evaluate A Single Prompt
Test Timeout      5 minutes

*** Variables ***
${MOCK_MODE}      ${False}

*** Test Cases ***
# Data-driven tests. The columns are [Test Case Name], [Prompt Text]
Fairness Prompt 1        ${wnba_fairness_prompts}[0]
Fairness Prompt 2        ${wnba_fairness_prompts}[1]
Fairness Prompt 3        ${wnba_fairness_prompts}[2]
Fairness Prompt 4        ${wnba_fairness_prompts}[3]
Fairness Prompt 5        ${wnba_fairness_prompts}[4]
Fairness Prompt 6        ${wnba_fairness_prompts}[5]

Accuracy Prompt 1        ${wnba_accuracy_prompts}[0]
Accuracy Prompt 2        ${wnba_accuracy_prompts}[1]
Accuracy Prompt 3        ${wnba_accuracy_prompts}[2]
Accuracy Prompt 4        ${wnba_accuracy_prompts}[3]
Accuracy Prompt 5        ${wnba_accuracy_prompts}[4]
Accuracy Prompt 6        ${wnba_accuracy_prompts}[5]

Toxicity Prompt 1        ${wnba_toxicity_prompts}[0]
Toxicity Prompt 2        ${wnba_toxicity_prompts}[1]
Toxicity Prompt 3        ${wnba_toxicity_prompts}[2]
Toxicity Prompt 4        ${wnba_toxicity_prompts}[3]
Toxicity Prompt 5        ${wnba_toxicity_prompts}[4]
Toxicity Prompt 6        ${wnba_toxicity_prompts}[5]

*** Keywords ***
Evaluate A Single Prompt
    [Arguments]    ${prompt_text}
    [Documentation]    This keyword is a template that calls all APIs for a single prompt and runs evaluations.

    @{providers}=    Create List    grok    openai    anthropic    gemini

    FOR    ${provider}    IN    @{providers}
        Run Evaluations For A Single Provider    ${provider}    ${prompt_text}
    END

Run Evaluations For A Single Provider
    [Arguments]    ${provider}    ${prompt_text}
    [Documentation]    Runs the full test and evaluation cycle for one provider.

    ${tier}=    Set Variable    lite

    Log To Console    \n--- Testing ${provider.upper()} with prompt: ${prompt_text} ---

    # Step 1: Get the response from the API. The initial response is saved to the DB by this keyword.
    ${response_text}=    Run Test Against Provider And Tier
    ...    provider=${provider}
    ...    tier=${tier}
    ...    prompt=${prompt_text}
    ...    mock_mode=${MOCK_MODE}

    # Step 2: Run evaluations only if not in mock mode. Each of these keywords will now FAIL the test if the evaluation is not passed.
    Run Keyword If    not ${MOCK_MODE}
    ...    Run All Assertions
    ...    ${provider}
    ...    ${tier}
    ...    ${prompt_text}
    ...    ${response_text}

Run All Assertions
    [Arguments]    ${provider}    ${tier}    ${prompt_text}    ${response_text}
    [Documentation]    A wrapper keyword to run all evaluations for a single provider response.

    # --- DeepEval Assertions ---
    Evaluate Response For Toxicity    ${prompt_text}    ${response_text}
    Evaluate Response For Relevancy    ${prompt_text}    ${response_text}

    # --- LangTest Assertion (skip for Grok as it's not a supported hub) ---
    Run Keyword If    '${provider}' != 'grok'
    ...    Run Robustness Test With Langtest
    ...    provider=${provider}
    ...    tier=${tier}
    ...    prompt=${prompt_text}
