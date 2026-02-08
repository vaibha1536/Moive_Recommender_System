import pandas as pd
import streamlit as st
import pickle
import requests
import time


st.set_page_config(
    page_title="Movie Recommender System (Vaibhav)",
    layout="wide"
)



# -------------------------------
# TMDB Poster Fetch (SAFE VERSION)
# -------------------------------
@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {
        "api_key": "c692eb3f45f1c89f1cb04cc9a50a27b9",
        "language": "en-US"
    }
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    try:
        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        poster_path = data.get("poster_path")
        if poster_path:
            return "https://image.tmdb.org/t/p/w500" + poster_path
        else:
            return None

    except requests.exceptions.RequestException as e:
        print("TMDB request failed:", e)
        return None


# -------------------------------
# Recommendation Logic
# -------------------------------
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1]
    )

    recommended_movies = []
    recommended_movies_poster = []

    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_poster.append(fetch_poster(movie_id))
        time.sleep(0.2)  # prevent TMDB rate-limit issues

    return recommended_movies, recommended_movies_poster


# -------------------------------
# Load Data
# -------------------------------
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl', 'rb'))


# -------------------------------
# Streamlit UI
# -------------------------------
st.title("🎬 Movie Recommender System")

st.markdown("""
<style>
.movie-title {
    height: 3.2em;
    overflow: hidden;
    text-align: center;
    font-size: 16px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)




selected_movie_name = st.selectbox(
    "Select a movie:",
    movies['title'].values
)

if st.button("Recommend"):
    names, posters = recommend(selected_movie_name)

    cols = st.columns(5)

    for i, col in enumerate(cols):
        with col:
            st.text(names[i])
            if posters[i]:
                st.image(posters[i])
            else:
                st.write("Poster not available")
