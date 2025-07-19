*** Settings ***
Documentation     A simple 'Hello World' test to verify the Robot Framework setup.
Library           OperatingSystem

*** Test Cases ***
Verify Environment Is Ready
       Logs a welcome message and checks the Python version.
    Log To Console    \n--- Hello from Robot Framework! ---
    ${result}=    Run Process    python --version    shell=True
    Log To Console    Python Version: ${result.stdout}
    Log To Console    Robot Framework is correctly configured and running.
    Log To Console    -----------------------------------\n

Directory Should Exist
       Verifies that a key project folder exists.
       filesystem
    Log To Console    Checking for the 'explorations' directory...
    Directory Should Exist    ${CURDIR}/../explorations
    Log To Console    Success! The 'explorations' directory was found.

