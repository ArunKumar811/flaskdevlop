import os
from dotenv import load_dotenv
import google.generativeai as genai

def test_google_api_key():
    """
    A simple script to test if the Google AI Studio API key is working.
    """
    # 1. Load the environment variables from the .env file
    load_dotenv()
    
    # 2. Get the API key from the environment
    api_key = os.environ.get('GOOGLE_API_KEY')
    
    # 3. Check if the key was found
    if not api_key:
        print("--- TEST FAILED ---")
        print("ERROR: GOOGLE_API_KEY not found in .env file.")
        print("Please make sure your .env file is in the same directory and has the correct variable name.")
        return

    print("--- Starting API Test ---")
    print("API Key found in .env file.")

    try:
        # 4. Configure the generative AI client with the key
        genai.configure(api_key=api_key)
        
        # 5. Create an instance of the model
        # Using the latest stable model name
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # 6. Send a simple prompt to the model
        print("Sending a test prompt to the Gemini model...")
        response = model.generate_content("What is the capital of France?")
        
        # 7. Print the response from the AI
        print("\n--- TEST SUCCESSFUL ---")
        print("Successfully received a response from the API:")
        print(f"AI Response: {response.text}")

    except Exception as e:
        # 8. If any part of the process fails, print a detailed error
        print("\n--- TEST FAILED ---")
        print(f"An error occurred: {e}")
        print("Troubleshooting steps:")
        print("1. Double-check that your API key is correct and has no typos.")
        print("2. Ensure the 'Vertex AI API' is enabled in your Google Cloud project.")
        print("3. Make sure your Google Cloud project is linked to a billing account.")

# Run the test function
if __name__ == "__main__":
    test_google_api_key()
