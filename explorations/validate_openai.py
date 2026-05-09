# validate_openai.py
import os
import openai
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def validate_openai_model_access(model_name="gpt-4o-mini"):
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        logging.error("Error: OPENAI_API_KEY environment variable is not set.")
        print("\nACTION REQUIRED: Please set your OPENAI_API_KEY environment variable.")
        return False

    logging.info(f"Attempting to validate OPENAI_API_KEY for model: {model_name}")

    try:
        client = openai.OpenAI(api_key=api_key)

        # Make a small, simple chat completion request
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": "Say 'DeepEval test handshake successful!'"}
            ],
            max_tokens=20,  # Keep it small to minimize token usage for validation
            timeout=10  # Add a timeout
        )

        content = response.choices[0].message.content.strip()
        logging.info(f"SUCCESS: Received response from {model_name}: '{content}'")
        print(f"\nVALIDATION SUCCESS: Your OPENAI_API_KEY is working for {model_name}.")
        print(f"Response: {content}")
        return True

    except openai.APIStatusError as e:
        # Handles 4xx and 5xx errors (e.g., 401 Unauthorized, 404 Not Found, 429 Rate Limit, 500 Server Error)
        if e.status_code == 401:
            logging.error(f"Error 401: Unauthorized. Your API key might be invalid or expired. Details: {e.response}")
            print("\nVALIDATION FAILED: Invalid or expired API key. Please check your key on platform.openai.com.")
        elif e.status_code == 404 and "model" in str(e).lower():
            logging.error(
                f"Error 404: Model not found. You might not have access to '{model_name}'. Details: {e.response}")
            print(f"\nVALIDATION FAILED: Access denied to model '{model_name}'. Check your OpenAI account permissions.")
        elif e.status_code == 429:
            error_msg = e.response.json().get('error', {}).get('message', 'Rate limit or quota exceeded.')
            logging.error(f"Error 429: Rate Limit / Quota Exceeded. Message: {error_msg}. Details: {e.response}")
            print(
                "\nVALIDATION FAILED: Rate limit or quota exceeded. Check your usage and billing on platform.openai.com.")
        else:
            logging.error(f"OpenAI API error (Status {e.status_code}): {e.message}", exc_info=True)
            print(f"\nVALIDATION FAILED: An OpenAI API error occurred (Status {e.status_code}). See logs for details.")
        return False
    except openai.APITimeoutError as e:
        logging.error(f"OpenAI API Timeout Error: {e}", exc_info=True)
        print("\nVALIDATION FAILED: OpenAI API call timed out. Check your internet connection or try again.")
        return False
    except openai.APIConnectionError as e:
        logging.error(f"OpenAI API Connection Error: {e}", exc_info=True)
        print("\nVALIDATION FAILED: Could not connect to OpenAI API. Check your internet connection.")
        return False
    except openai.AuthenticationError as e:
        logging.error(f"OpenAI API Authentication Error: {e}. Check your OPENAI_API_KEY.", exc_info=True)
        print("\nVALIDATION FAILED: Authentication Error. Your OPENAI_API_KEY is likely incorrect or problematic.")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred during OpenAI API validation: {e}", exc_info=True)
        print(f"\nVALIDATION FAILED: An unexpected error occurred. See logs for details.")
        return False


if __name__ == "__main__":
    # Ensure OPENAI_API_KEY is set in your environment before running this script
    # For example:
    # Windows PowerShell: $env:OPENAI_API_KEY="sk-..."
    # Linux/macOS: export OPENAI_API_KEY="sk-..."

    validate_openai_model_access("gpt-4o-mini")