
import os
import json
import pandas as pd
import google.generativeai as genai

# --- NLTK setup ---
import nltk

# Ensure 'punkt_tab' tokenizer is available
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    print("Downloading NLTK 'punkt_tab' tokenizer...")
    nltk.download('punkt_tab')


def generate_jobs_with_ai(keywords, num_jobs=5, api_key=None):
    """
    Uses Google Gemini 2.5 Flash to generate realistic job postings
    and returns a pandas DataFrame with the required columns.
    """

    # 1️⃣ Get API key from argument (fallback to environment variable)
    if api_key is None:
        api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        print("ERROR: GOOGLE_API_KEY not provided or not found in environment.")
        return pd.DataFrame()

    # 2️⃣ Configure the Google Generative AI client
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        print(f"Error configuring Google AI: {e}")
        return pd.DataFrame()

    # 3️⃣ Prepare prompt with structured JSON output
    prompt = f"""
    Generate a list of {num_jobs} realistic job postings for a candidate with skills in: {', '.join(keywords)}.

    IMPORTANT: Return the data as a valid JSON array of objects. Do not include any text or formatting before or after the JSON array.
    Each JSON object MUST have the following keys:
    - "title"
    - "company"
    - "location"
    - "description"
    - "requirements"
    - "min_experience" (number, e.g., 2 or 5)

    Example:
    [
      {{
        "title": "Data Scientist",
        "company": "Innovate AI",
        "location": "Remote",
        "description": "We are seeking a talented Data Scientist...",
        "requirements": "Python, SQL, Machine Learning",
        "min_experience": 3
      }}
    ]
    """

    try:
        # 4️⃣ Use Gemini 2.5 Flash to generate jobs
        model = genai.GenerativeModel('gemini-2.5-flash')
        print("Generating jobs with Gemini 2.5 Flash...")
        response = model.generate_content(prompt)

        # 5️⃣ Parse JSON from AI response
        json_text = response.text.strip()
        start = json_text.find('[')
        end = json_text.rfind(']')
        if start != -1 and end != -1:
            json_str = json_text[start:end+1]
            jobs_list = json.loads(json_str)
        else:
            raise ValueError("No valid JSON array found in AI response.")

        # 6️⃣ Convert to pandas DataFrame
        jobs_df = pd.DataFrame(jobs_list)

        # 7️⃣ Ensure 'min_experience' is numeric
        if 'min_experience' in jobs_df.columns:
            jobs_df['min_experience'] = pd.to_numeric(jobs_df['min_experience'], errors='coerce').fillna(0)

        print(f"Successfully generated {len(jobs_df)} jobs from Google AI.")
        return jobs_df

    except Exception as e:
        print(f"An error occurred while generating jobs with Google AI: {e}")
        if 'response' in locals():
            print("--- AI Raw Response ---")
            print(response.text)
            print("----------------------")
        return pd.DataFrame()


# --- Test block for standalone execution ---
if __name__ == "__main__":
    test_keywords = ["Python", "Data Science", "AI"]
    df_jobs = generate_jobs_with_ai(test_keywords)
    print(df_jobs)
