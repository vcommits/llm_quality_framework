*** Settings ***
Documentation     A simple test to verify the connection to our Python keyword library.
Library           llm_tests.LLMKeywords.py

*** Test Cases ***
Should Be Able To Call A Custom Python Keyword
    ${response}=    Call Grok API With Mock    This is a simple test prompt.
    Log To Console    \nKeyword Response: ${response}
    Should Not Be Empty    ${response}

