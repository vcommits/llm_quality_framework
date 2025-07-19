*** Settings ***
Documentation     A simple 'Hello World' test to verify the Robot Framework setup.
Library           OperatingSystem

*** Test Cases ***
Verify Environment Is Ready
    Log To Console    \n--- Hello from Robot Framework! ---
    ${python_version}=    Run    python --version
    Log To Console    Python Version: ${python_version}
    Log To Console    Robot Framework is correctly configured and running.
    Log To Console    -----------------------------------\n

Directory Should Exist
    Log To Console    Checking for the 'explorations' directory...
    Directory Should Exist    ${CURDIR}/../explorations
    Log To Console    Success! The 'explorations' directory was found.

