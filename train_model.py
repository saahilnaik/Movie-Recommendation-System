"""
Model Training Script
Generates pickle files for similarity matrix and processed movies data.
Run this once to create model artifacts.
"""

import pandas as pd
import numpy as np
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path

# Setup paths
project_root = Path(__file__).parent
data_path = project_root / "movies.csv"
model_path = project_root / "model"

print("Loading data...")
data = pd.read_csv(data_path)

print(f"Dataset shape: {data.shape}")
print(f"Columns: {list(data.columns)}")

# Select relevant features for recommendation
relevant_features = ['genres', 'keywords', 'tagline', 'cast', 'director']

# Fill null values
for feature in relevant_features:
    data[feature] = data[feature].fillna('')

print("Combining features...")
# Combine all features into one field
combined_features = (data['genres'] + ' ' + 
                    data['keywords'] + ' ' + 
                    data['tagline'] + ' ' + 
                    data['cast'] + ' ' + 
                    data['director'])

print("Vectorizing text features...")
vectorizer = TfidfVectorizer()
feature_vectors = vectorizer.fit_transform(combined_features)
print(f"Feature vectors shape: {feature_vectors.shape}")

print("Computing cosine similarity...")
similarity = cosine_similarity(feature_vectors)
print(f"Similarity matrix shape: {similarity.shape}")

print("Saving model artifacts...")
# Save similarity matrix
with open(model_path / "similarity.pkl", "wb") as f:
    pickle.dump(similarity, f)

# Save movies dataframe with necessary columns
movies_to_save = data[['title', 'id', 'genres', 'vote_average', 'overview']].copy()
with open(model_path / "movies.pkl", "wb") as f:
    pickle.dump(movies_to_save, f)

print("✅ Model training complete!")
print(f"   Saved: {model_path / 'similarity.pkl'}")
print(f"   Saved: {model_path / 'movies.pkl'}")
print(f"   Total movies in database: {len(movies_to_save)}")
