*** Settings ***
Documentation     A simple test to verify the connection to our Python keyword library.
Library           tests.LLMKeywords

*** Test Cases ***
Should Be Able To Call A Custom Python Keyword
    [Documentation]    Calls a keyword from the local library with mock mode enabled.

    ${response}=    Call Grok API    This is a simple test prompt.    mock_mode=${True}
    Log To Console    \nKeyword Response: ${response}
    Should Not Be Empty    ${response}
