*** Settings ***
Documentation     A suite of tests for evaluating LLM responses to WNBA-related prompts.
Library           llm_tests.LLMKeywords
Variables         ../config/wnba_prompts.yaml
Suite Setup       Log To Console    --- Preparing the WNBA Test Suite ---
Suite Teardown    Log To Console    --- Cleaning Up the WNBA Test Suite ---
# The Test Template will be applied to each test case below.
Test Template     Evaluate A Single Prompt

*** Variables ***
# This can be overridden from the command line, e.g., -v MOCK_MODE:True
${MOCK_MODE}      ${False}

*** Test Cases ***
# This is the standard data-driven testing approach in Robot Framework.
# The first column is the Test Case Name. The columns that follow are the
# arguments that get passed to the "Evaluate A Single Prompt" template keyword.
# The correct syntax to access a single list item by index is ${list_name}[index].
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
    [Documentation]    This keyword is a template that calls all APIs for a single prompt and logs the results.

    # --- Test Grok ---
    ${grok_response}=    Call Grok API    prompt=${prompt_text}    mock_mode=${MOCK_MODE}
    Should Not Be Empty    ${grok_response}
    Log To Console    \n--- Grok Response ---\n${grok_response}\n---------------------\n

    # --- Test OpenAI ---
    ${openai_response}=    Call OpenAI API    prompt=${prompt_text}    mock_mode=${MOCK_MODE}
    Should Not Be Empty    ${openai_response}
    Log To Console    \n--- OpenAI Response ---\n${openai_response}\n-----------------------\n

    # --- Test Anthropic ---
    ${anthropic_response}=    Call Anthropic API    prompt=${prompt_text}    mock_mode=${MOCK_MODE}
    Should Not Be Empty    ${anthropic_response}
    Log To Console    \n--- Anthropic Response ---\n${anthropic_response}\n--------------------------\n

    # --- Test Gemini ---
    ${gemini_response}=    Call Gemini API    prompt=${prompt_text}    mock_mode=${MOCK_MODE}
    Should Not Be Empty    ${gemini_response}
    Log To Console    \n--- Gemini Response ---\n${gemini_response}\n-----------------------\n

