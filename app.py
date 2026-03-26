"""
Movie Recommendation System - Streamlit App
Netflix-inspired UI for movie discovery
"""

import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import pickle

from recommender import recommend
from fetch_poster import fetch_poster

# Load custom CSS
@st.cache_resource
def load_css():
    """Load custom CSS for styling"""
    css_path = Path(__file__).parent / "assets" / "styles.css"
    if css_path.exists():
        with open(css_path, "r") as f:
            return f"<style>{f.read()}</style>"
    return ""


def load_all_movies():
    """Load all movies for the selectbox"""
    model_path = Path(__file__).parent / "model"
    try:
        with open(model_path / "movies.pkl", "rb") as f:
            movies = pickle.load(f)
        return sorted(movies['title'].tolist())
    except FileNotFoundError:
        return []
    except (pickle.UnpicklingError, EOFError):
        st.error(
            "⚠️ Model file appears corrupted or not downloaded properly. "
            "If you are using Git LFS, run `git lfs pull` and restart the app. "
            "If the problem persists, re-clone the repository."
        )
        st.stop()


# Page Configuration
st.set_page_config(
    page_title="🎬 Movie Recommender",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS
st.markdown(load_css(), unsafe_allow_html=True)

# Custom Title with styling
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="color: #E50914; font-size: 3rem; margin: 0; font-family: 'Bebas Neue', sans-serif; letter-spacing: 2px;">
            🎬 MOVIE RECOMMENDATION SYSTEM
        </h1>
        <p style="color: #B3B3B3; font-size: 1.1rem; margin-top: 0.5rem;">
            Discover movies tailored to your taste
        </p>
        <hr style="border: 1px solid #E50914; margin: 1.5rem 0;">
    </div>
    """,
    unsafe_allow_html=True
)

# Sidebar
with st.sidebar:
    st.markdown(
        """
        <h3 style="color: #E50914;">ℹ️ About</h3>
        <p>This recommender uses <b>content-based filtering</b> to suggest movies similar to your favorite pick.</p>
        <p><b>How it works:</b></p>
        <ul>
          <li>Analyzes genres, keywords, cast, director, and storylines</li>
          <li>Calculates similarity between movies</li>
          <li>Returns 5 most similar recommendations</li>
        </ul>
        <hr style="border: 1px solid #333;">
        <p><small>Powered by TF-IDF & Cosine Similarity</small></p>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        """
        <p style="margin-top: 2rem; text-align: center; color: #B3B3B3;">
            <a href="https://github.com/saahilnaik" target="_blank" style="color: #E50914; text-decoration: none;">
                🔗 GitHub
            </a>
        </p>
        """,
        unsafe_allow_html=True
    )

# Main Content
col1, col2, col3 = st.columns([2, 1, 1], gap="large")

# Load all movies
movie_list = load_all_movies()

if not movie_list:
    st.error(
        "⚠️ Model files not found! Please run `train_model.py` first to generate model artifacts."
    )
    st.stop()

# Movie Selection
with col1:
    selected_movie = st.selectbox(
        "🎥 Select a movie you love:",
        options=movie_list,
        index=0 if movie_list else None,
        help="Start typing to search for movies"
    )

# Get Recommendations Button
with col2:
    if st.button("🎯 Get Recommendations", use_container_width=True, key="recommend_btn"):
        st.session_state.show_recommendations = True
    else:
        if "show_recommendations" not in st.session_state:
            st.session_state.show_recommendations = False

with col3:
    if st.button("🎲 Surprise Me!", use_container_width=True, key="surprise_btn"):
        import random
        selected_movie = random.choice(movie_list)
        st.session_state.show_recommendations = True
        st.rerun()

# Display Recommendations
if st.session_state.get("show_recommendations", False):
    st.markdown("<hr style='border: 1px solid #E50914; margin: 2rem 0;'>", unsafe_allow_html=True)
    
    with st.spinner("🎬 Finding perfect matches..."):
        try:
            # Get recommendations
            recommendations = recommend(selected_movie, num_recommendations=5)
            
            # Fetch posters in parallel
            def fetch_with_id(rec):
                return fetch_poster(rec['movie_id']), rec
            
            poster_urls = {}
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = {executor.submit(fetch_with_id, rec): rec['movie_id'] 
                          for rec in recommendations}
                
                for future in as_completed(futures):
                    try:
                        url, rec = future.result()
                        poster_urls[rec['movie_id']] = url
                    except Exception:
                        pass
            
            # Display recommendations in columns
            cols = st.columns(5, gap="small")
            
            for col, movie in zip(cols, recommendations):
                with col:
                    poster_url = poster_urls.get(movie['movie_id'], 
                                                 "https://via.placeholder.com/300x450?text=Poster+Not+Available")
                    
                    st.markdown(
                        f"""
                        <div class="movie-card">
                            <img src="{poster_url}" alt="{movie['title']}" class="movie-poster">
                            <div class="movie-title">{movie['title']}</div>
                            <div class="movie-rating">⭐ {movie['rating']}/10</div>
                            <div class="movie-genres">{movie['genres'][:30]}...</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            
            # Show details in expandable sections
            st.markdown("### 📋 Recommendation Details")
            
            for i, movie in enumerate(recommendations, 1):
                with st.expander(f"**{i}. {movie['title']}** ⭐ {movie['rating']}/10"):
                    st.write(f"**Genres:** {movie['genres']}")
                    st.write(f"**Rating:** {movie['rating']}/10")
                    st.write(f"**Overview:** {movie['overview']}")
            
        except ValueError as e:
            st.error(f"❌ {str(e)}")
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")

# Footer
st.markdown(
    """
    <hr style="border: 1px solid #333; margin-top: 3rem;">
    <div style="text-align: center; color: #B3B3B3; font-size: 0.9rem; padding: 1rem;">
        <p>Built with ❤️ using Streamlit | Data powered by TMDB</p>
    </div>
    """,
    unsafe_allow_html=True
)
