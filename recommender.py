"""
Movie Recommendation Engine
Loads pre-trained models and generates recommendations.
"""

import pickle
import difflib
from pathlib import Path
import streamlit as st


@st.cache_resource
def load_models():
    """
    Load similarity matrix and movies data.
    Uses Streamlit cache to load only once per session.
    
    Returns:
        tuple: (similarity_matrix, movies_df, list_of_titles)
    """
    model_path = Path(__file__).parent / "model"
    try:
        # Load similarity matrix
        with open(model_path / "similarity.pkl", "rb") as f:
            similarity = pickle.load(f)

        # Load movies dataframe
        with open(model_path / "movies.pkl", "rb") as f:
            movies = pickle.load(f)

    except FileNotFoundError as e:
        raise ValueError(
            f"Model files not found. Ensure model directory exists and contains similarity.pkl and movies.pkl. {e}"
        )
    except (pickle.UnpicklingError, EOFError) as e:
        raise ValueError(
            "Model file corrupted or not downloaded properly. "
            "Run `git lfs pull` and restart the app. "
            f"Error: {e}"
        )

    # Create title list for matching
    titles = movies['title'].tolist()

    return similarity, movies, titles


def recommend(movie_title: str, num_recommendations: int = 5) -> list:
    """
    Generate movie recommendations based on content similarity.
    
    Args:
        movie_title (str): Exact or partial movie title
        num_recommendations (int): Number of recommendations to return
    
    Returns:
        list: List of dicts with 'title' and 'movie_id' of recommended movies
    
    Raises:
        ValueError: If movie not found or model files missing
    """
    try:
        similarity, movies, titles = load_models()
    except FileNotFoundError as e:
        raise ValueError(
            f"Model files not found! Ensure model/similarity.pkl and model/movies.pkl exist. Error: {e}"
        )
    
    # Find close match using difflib
    close_matches = difflib.get_close_matches(movie_title, titles, n=1, cutoff=0.6)
    
    if not close_matches:
        raise ValueError(f"Movie '{movie_title}' not found in database.")
    
    matched_title = close_matches[0]
    
    # Find index of matched movie
    matched_index = movies[movies['title'] == matched_title].index[0]
    
    # Get similarity scores
    similarity_scores = list(enumerate(similarity[matched_index]))
    
    # Sort by similarity (descending), excluding the input movie itself
    sorted_movies = sorted(similarity_scores, key=lambda x: x[1], reverse=True)[1:num_recommendations + 1]
    
    # Build recommendation list
    recommendations = []
    for idx, score in sorted_movies:
        movie_row = movies.iloc[idx]
        recommendations.append({
            "title": movie_row['title'],
            "movie_id": int(movie_row['id']),
            "genres": movie_row['genres'],
            "rating": float(movie_row['vote_average']),
            "overview": movie_row['overview']
        })
    
    return recommendations


if __name__ == "__main__":
    # Example usage for standalone testing
    test_movie = "Avatar"
    try:
        results = recommend(test_movie, num_recommendations=5)
        print(f"\n✅ Recommendations for '{test_movie}':\n")
        for i, movie in enumerate(results, 1):
            print(f"{i}. {movie['title']} (ID: {movie['movie_id']}, Rating: {movie['rating']})")
    except ValueError as e:
        print(f"❌ Error: {e}")
