*** Settings ***
Documentation     A test suite for running DeepTeam red teaming scenarios.
...               This suite uses the custom keywords defined in LLMKeywords.py
...               to execute tests against various LLM providers and attack methods.
Library           llm_tests.LLMKeywords

*** Variables ***
${CUSTOM_PROMPTS_FILE}    config/custom_jailbreaks.yaml

*** Test Cases ***
Hybrid Red Team on Gemini Lite
    [Documentation]    Runs a hybrid test against the Gemini 'lite' tier model.
    [Tags]    deepteam    real    hybrid    gemini
    Run Deepteam Red Teaming
    ...    api=gemini
    ...    tier=lite
    ...    attack=prompt_injection
    ...    custom_prompts_file=${CUSTOM_PROMPTS_FILE}

Hybrid Red Team on OpenAI Lite
    [Documentation]    Runs a hybrid test against the OpenAI 'lite' tier model.
    [Tags]    deepteam    real    hybrid    openai
    Run Deepteam Red Teaming
    ...    api=openai
    ...    tier=lite
    ...    attack=prompt_injection
    ...    custom_prompts_file=${CUSTOM_PROMPTS_FILE}

Hybrid Red Team on Claude Lite
    [Documentation]    Runs a hybrid test against the Anthropic Claude 'lite' tier model.
    [Tags]    deepteam    real    hybrid    claude
    Run Deepteam Red Teaming
    ...    api=claude
    ...    tier=lite
    ...    attack=prompt_injection
    ...    custom_prompts_file=${CUSTOM_PROMPTS_FILE}

Hybrid Red Team on Grok Mid
    [Documentation]    Runs a hybrid test against the Grok 'mid' tier model.
    [Tags]    deepteam    real    hybrid    grok
    Run Deepteam Red Teaming
    ...    api=grok
    ...    tier=mid
    ...    attack=prompt_injection
    ...    custom_prompts_file=${CUSTOM_PROMPTS_FILE}