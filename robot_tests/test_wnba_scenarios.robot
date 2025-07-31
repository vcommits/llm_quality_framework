*** Settings ***
Documentation     A data-driven test suite for evaluating LLM responses to WNBA-related prompts.
Library           llm_tests.LLMKeywords
Variables         ../config/wnba_prompts.yaml
Suite Setup       Log Suite Preparation Details
Suite Teardown    Log To Console    --- Cleaning Up the WNBA Test Suite ---
# The Test Template will be applied to each test case below.
Test Template     Evaluate A Single Prompt
Test Timeout      5 minutes    # Set a maximum execution time for each test case

*** Variables ***
# This can be overridden from the command line, e.g., -v MOCK_MODE:True
${MOCK_MODE}      ${False}

*** Test Cases ***
# This is the standard data-driven testing approach in Robot Framework.
# The first column is the Test Case Name. The columns that follow are the
# arguments that get passed to the "Evaluate A Single Prompt" template keyword.
# The correct syntax to access a single list item by index is ${list_name}[index].
Fairness Prompt 1        ${wnba_fairness_prompts}[0]    Fairness
Fairness Prompt 2        ${wnba_fairness_prompts}[1]    Fairness
Fairness Prompt 3        ${wnba_fairness_prompts}[2]    Fairness
Fairness Prompt 4        ${wnba_fairness_prompts}[3]    Fairness
Fairness Prompt 5        ${wnba_fairness_prompts}[4]    Fairness
Fairness Prompt 6        ${wnba_fairness_prompts}[5]    Fairness

Accuracy Prompt 1        ${wnba_accuracy_prompts}[0]    Accuracy
Accuracy Prompt 2        ${wnba_accuracy_prompts}[1]    Accuracy
Accuracy Prompt 3        ${wnba_accuracy_prompts}[2]    Accuracy
Accuracy Prompt 4        ${wnba_accuracy_prompts}[3]    Accuracy
Accuracy Prompt 5        ${wnba_accuracy_prompts}[4]    Accuracy
Accuracy Prompt 6        ${wnba_accuracy_prompts}[5]    Accuracy

Toxicity Prompt 1        ${wnba_toxicity_prompts}[0]    Toxicity
Toxicity Prompt 2        ${wnba_toxicity_prompts}[1]    Toxicity
Toxicity Prompt 3        ${wnba_toxicity_prompts}[2]    Toxicity
Toxicity Prompt 4        ${wnba_toxicity_prompts}[3]    Toxicity
Toxicity Prompt 5        ${wnba_toxicity_prompts}[4]    Toxicity
Toxicity Prompt 6        ${wnba_toxicity_prompts}[5]    Toxicity

*** Keywords ***
Log Suite Preparation Details
    [Documentation]    Logs details about the loaded variables and suite preparation.
    Log To Console    --- Preparing the WNBA Test Suite ---
    Log To Console    Fairness Prompts Loaded: ${wnba_fairness_prompts}
    Log To Console    Accuracy Prompts Loaded: ${wnba_accuracy_prompts}
    Log To Console    Toxicity Prompts Loaded: ${wnba_toxicity_prompts}
    Log To Console    MOCK_MODE: ${MOCK_MODE}
    Log To Console    --- Suite Preparation Complete ---

Evaluate A Single Prompt
    [Arguments]    ${prompt_text}    ${test_type}
    [Documentation]    This keyword is a template that calls all APIs for a single prompt and logs the results.

    # Define the common LangTest config as a JSON string
    ${langtest_config_json_string}=    Set Variable    {"tests": {"robustness": {"typo": {"min_pass_rate": 0.7}}}}
    ${system_prompt}=    Set Variable    None # Default system prompt for now, can be customized per test

    # --- Test Grok ---
    Log To Console    \n--- Testing Grok with prompt: ${prompt_text} ---
    ${grok_model}=    Set Variable    grok-3-mini
    ${grok_tier}=     Set Variable    lite
    ${grok_response}=    Run Test Against Provider And Tier    grok    ${grok_tier}    ${prompt_text}    system_prompt=${system_prompt}    mock_mode=${MOCK_MODE}
    Log To Console    Grok Response Received: ${grok_response}
    Evaluate Response For Toxicity    ${test_type}-grok-${prompt_text}    grok    ${grok_model}    ${grok_tier}    ${test_type}    ${prompt_text}    ${system_prompt}    ${grok_response}
    # Integrate LangTest evaluation for Grok (PERMANENTLY COMMENTED OUT as there is no 'grok' hub in LangTest)
    # ${grok_sample_data}=    Create Dictionary    text=${prompt_text}    expected_results=${grok_response}
    # ${langtest_grok_data}=    Create List          ${grok_sample_data}
    # Run Langtest Harness And Save Results    ${test_type}-grok-${prompt_text}    grok    ${grok_model}    ${grok_tier}    ${test_type}    ${prompt_text}    ${system_prompt}    ${grok_response}    ${langtest_config_json_string}    ${langtest_grok_data}
    Log To Console    \n--- Grok Response ---\n${grok_response}\n---------------------\n

    # --- Test OpenAI ---
    Log To Console    \n--- Testing OpenAI with prompt: ${prompt_text} ---
    ${openai_model}=    Set Variable    gpt-4o-mini
    ${openai_tier}=     Set Variable    lite
    ${openai_response}=    Run Test Against Provider And Tier    openai    ${openai_tier}    ${prompt_text}    system_prompt=${system_prompt}    mock_mode=${MOCK_MODE}
    Log To Console    OpenAI Response Received: ${openai_response}
    Evaluate Response For Toxicity    ${test_type}-openai-${prompt_text}    openai    ${openai_model}    ${openai_tier}    ${test_type}    ${prompt_text}    ${system_prompt}    ${openai_response}
    # Integrate LangTest evaluation for OpenAI
    ${openai_sample_data}=    Create Dictionary    text=${prompt_text}    expected_results=${openai_response}
    ${langtest_openai_data}=    Create List          ${openai_sample_data}
    Run Langtest Harness And Save Results    ${test_type}-openai-${prompt_text}    openai    ${openai_model}    ${openai_tier}    ${test_type}    ${prompt_text}    ${system_prompt}    ${openai_response}    ${langtest_config_json_string}    ${langtest_openai_data}
    Log To Console    \n--- OpenAI Response ---\n${openai_response}\n-----------------------\n

    # --- Test Anthropic ---
    Log To Console    \n--- Testing Anthropic with prompt: ${prompt_text} ---
    ${anthropic_model}=    Set Variable    claude-3-haiku-20240307
    ${anthropic_tier}=     Set Variable    lite
    ${anthropic_response}=    Run Test Against Provider And Tier    anthropic    ${anthropic_tier}    ${prompt_text}    system_prompt=${system_prompt}    mock_mode=${MOCK_MODE}
    Log To Console    Anthropic Response Received: ${anthropic_response}
    Evaluate Response For Toxicity    ${test_type}-anthropic-${prompt_text}    anthropic    ${anthropic_model}    ${anthropic_tier}    ${test_type}    ${prompt_text}    ${system_prompt}    ${anthropic_response}
    # Integrate LangTest evaluation for Anthropic
    ${anthropic_sample_data}=    Create Dictionary    text=${prompt_text}    expected_results=${anthropic_response}
    ${langtest_anthropic_data}=    Create List          ${anthropic_sample_data}
    Run Langtest Harness And Save Results    ${test_type}-anthropic-${prompt_text}    anthropic    ${anthropic_model}    ${anthropic_tier}    ${test_type}    ${prompt_text}    ${system_prompt}    ${anthropic_response}    ${langtest_config_json_string}    ${langtest_anthropic_data}
    Log To Console    \n--- Anthropic Response ---\n${anthropic_response}\n--------------------------\n

    # --- Test Gemini ---
    Log To Console    \n--- Testing Gemini with prompt: ${prompt_text} ---
    ${gemini_model}=    Set Variable    gemini-1.5-flash-latest
    ${gemini_tier}=     Set Variable    lite
    ${gemini_response}=    Run Test Against Provider And Tier    gemini    ${gemini_tier}    ${prompt_text}    system_prompt=${system_prompt}    mock_mode=${MOCK_MODE}
    Log To Console    Gemini Response Received: ${gemini_response}
    Evaluate Response For Toxicity    ${test_type}-gemini-${prompt_text}    gemini    ${gemini_model}    ${gemini_tier}    ${test_type}    ${prompt_text}    ${system_prompt}    ${gemini_response}
    # Integrate LangTest evaluation for Gemini
    ${gemini_sample_data}=    Create Dictionary    text=${prompt_text}    expected_results=${gemini_response}
    ${langtest_gemini_data}=    Create List          ${gemini_sample_data}
    Run Langtest Harness And Save Results    ${test_type}-gemini-${prompt_text}    gemini    ${gemini_model}    ${gemini_tier}    ${test_type}    ${prompt_text}    ${system_prompt}    ${gemini_response}    ${langtest_config_json_string}    ${langtest_gemini_data}
    Log To Console    \n--- Gemini Response ---\n${gemini_response}\n-----------------------\n

# Helper keyword to generate UUID
Generate UUID
    ${uuid}=    Evaluate    str(uuid.uuid4())    modules=uuid
    Return From Keyword    ${uuid}