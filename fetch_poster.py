"""
TMDB Poster Fetcher
Fetches movie posters from The Movie Database API.
"""

import os
import requests
import logging
from typing import Optional

from dotenv import load_dotenv

# Load .env config, if present
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# TMDB API Configuration
TMDB_BASE_URL = "https://api.themoviedb.org/3/movie"
POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"

# Fallback placeholder image
PLACEHOLDER_URL = "https://via.placeholder.com/300x450?text=Poster+Not+Available"


def fetch_poster(movie_id: int) -> str:
    """
    Fetch movie poster URL from TMDB API.
    
    Args:
        movie_id (int): TMDB movie ID
    
    Returns:
        str: Full poster image URL or placeholder if unavailable
    
    Note:
        - Reads TMDB_API_KEY from environment variables
        - Returns placeholder on any failure without crashing
        - Includes retry logic with timeout
    """
    api_key = os.getenv("TMDB_API_KEY")
    
    if not api_key:
        logger.warning("TMDB_API_KEY not set in environment. Returning placeholder.")
        return PLACEHOLDER_URL
    
    url = f"{TMDB_BASE_URL}/{movie_id}"
    params = {"api_key": api_key}
    
    try:
        # Fetch with timeout and retry logic
        response = requests.get(url, params=params, timeout=2)
        response.raise_for_status()
        
        data = response.json()
        
        # Construct poster URL
        poster_path = data.get("poster_path")
        if poster_path:
            return f"{POSTER_BASE_URL}{poster_path}"
        else:
            logger.warning(f"No poster found for movie ID {movie_id}")
            return PLACEHOLDER_URL
            
    except requests.exceptions.Timeout:
        logger.warning(f"Request timeout for movie ID {movie_id}")
        return PLACEHOLDER_URL
    except requests.exceptions.RequestException as e:
        logger.warning(f"Failed to fetch poster for movie ID {movie_id}: {e}")
        return PLACEHOLDER_URL
    except ValueError:
        # JSON decode error
        logger.warning(f"Invalid JSON response for movie ID {movie_id}")
        return PLACEHOLDER_URL
    except Exception as e:
        logger.warning(f"Unexpected error fetching poster for movie ID {movie_id}: {e}")
        return PLACEHOLDER_URL


if __name__ == "__main__":
    # Example usage for testing
    # Set your API key: export TMDB_API_KEY="your_key_here"
    test_id = 19995  # Avatar
    url = fetch_poster(test_id)
    print(f"Poster URL for movie ID {test_id}: {url}")
    