# config.py

import os
from dotenv import load_dotenv

load_dotenv()

# --- ADD THIS LINE FOR DEBUGGING ---
print(f"Key from os.environ: {os.environ.get('GOOGLE_API_KEY')}")
# ------------------------------------

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///job_recommender.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
