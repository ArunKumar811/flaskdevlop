import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem import PorterStemmer
import nltk

# Download necessary NLTK data
nltk.download('punkt')

class JobRecommender:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.stemmer = PorterStemmer()
        self.jobs_df = None
        self.tfidf_matrix = None
        
    def preprocess(self, text):
        """Preprocess text by tokenizing and stemming."""
        if pd.isna(text):
            return ""
        tokens = nltk.word_tokenize(text.lower())
        return " ".join([self.stemmer.stem(token) for token in tokens])
    
    def fit(self, jobs_df):
        """Fit the model on the jobs data."""
        self.jobs_df = jobs_df.copy()
        
        # Preprocess job descriptions and requirements
        self.jobs_df['processed_description'] = self.jobs_df['description'].apply(self.preprocess)
        self.jobs_df['processed_requirements'] = self.jobs_df['requirements'].apply(self.preprocess)
        
        # Create a combined text field for vectorization
        self.jobs_df['combined_text'] = (
            self.jobs_df['processed_description'] + ' ' + 
            self.jobs_df['processed_requirements'] + ' ' + 
            self.jobs_df['title'].apply(self.preprocess)
        )
        
        # Generate TF-IDF matrix
        self.tfidf_matrix = self.vectorizer.fit_transform(self.jobs_df['combined_text'])
        
    def recommend(self, user_profile, num_recommendations=5):
        """Generate job recommendations based on user profile."""
        skills = user_profile['skills']
        experience = user_profile.get('experience', 0)
        preferences = user_profile.get('preferences', [])
        
        # Create a user query based on skills and preferences
        user_query = ' '.join(skills) + ' ' + ' '.join(preferences)
        user_query = self.preprocess(user_query)
        
        # Transform user query to TF-IDF space
        user_vector = self.vectorizer.transform([user_query])
        
        # Calculate similarity scores
        similarity_scores = cosine_similarity(user_vector, self.tfidf_matrix).flatten()
        
        # Filter jobs based on experience
        experience_mask = self.jobs_df['min_experience'] <= experience
        filtered_indices = [i for i, matches in enumerate(experience_mask) if matches]
        filtered_scores = [similarity_scores[i] for i in filtered_indices]
        
        if not filtered_indices:
            return []
        
        # Get top recommendations
        top_indices = np.argsort(filtered_scores)[-num_recommendations:][::-1]
        recommended_jobs = [self.jobs_df.iloc[filtered_indices[i]] for i in top_indices]
        
        return recommended_jobs
