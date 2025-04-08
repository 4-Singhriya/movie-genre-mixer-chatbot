import google.generativeai as genai
import random
import difflib
import re
from API import API_KEY_GEMINI, API_KEY_TMDB
import requests

genai.configure(api_key=API_KEY_GEMINI)
model = genai.GenerativeModel('gemini-1.5-flash')

WATCHLIST = []

GENRES_LIST = [
    "action", "adventure", "animation", "biography", "comedy", "crime", "documentary",
    "drama", "family", "fantasy", "film-noir", "history", "horror", "music", "musical",
    "mystery", "romance", "sci-fi", "short", "sport", "superhero", "thriller", "war", "western"
]

def fetch_tmdb_details(title):
    url = f"https://api.themoviedb.org/3/search/movie?query={title}&api_key={API_KEY_TMDB}"
    response = requests.get(url).json()
    if response.get("results"):
        movie = response["results"][0]
        return {
            "title": movie.get("title", title),
            "release_date": movie.get("release_date", "N/A"),
            "language": movie.get("original_language", "N/A").upper(),
            "country": movie.get("origin_country", ["N/A"])[0],
            "popularity": round(movie.get("popularity", 0.0), 4),
            "alt_title": movie.get("original_title", title),
            "overview": movie.get("overview", "")
        }
    return {
        "title": title, "release_date": "N/A", "language": "N/A",
        "country": "N/A", "popularity": "N/A", "alt_title": "N/A",
        "overview": ""
    }

def extract_genres(user_input):
    user_input = user_input.lower()
    user_words = re.findall(r"\w+", user_input)
    matched_genres = set()
    for word in user_words:
        closest = difflib.get_close_matches(word, GENRES_LIST, n=1, cutoff=0.8)
        if closest:
            matched_genres.add(closest[0])
    return list(matched_genres)

def fetch_gemini_movies(prompt):
    response = model.generate_content(prompt)
    movies = re.findall(r"\*{1,2}(.+?)\*{1,2}", response.text)
    return [movie.strip().rstrip('.') for movie in movies if len(movie.strip()) > 2]

def get_movies_by_genre(genres_or_prompt):
    if isinstance(genres_or_prompt, list):
        prompt = f"Suggest 5 movies that fit these genres: {', '.join(genres_or_prompt)}. For each, include:\nTitle: <Movie Title>\nNarrative: <Short description>"
    else:
        prompt = f"Suggest 5 movies for this query: '{genres_or_prompt}'. Format each as:\nTitle: <Movie Title>\nNarrative: <Short description>"

    try:
        response = model.generate_content(prompt)
        if not response.text:
            return []
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return []

    pattern = r"Title:\s*(.+?)\s*Narrative:\s*(.+?)(?=Title:|$)"
    matches = re.findall(pattern, response.text, re.DOTALL)

    movies = []
    for title, narrative in matches:
        clean_title = title.strip().strip("**").strip()
        clean_narrative = narrative.strip().replace('\n', ' ')
        if clean_title:
            movies.append({
                "title": clean_title,
                "narrative": clean_narrative
            })

    return movies


def random_mix_movies():
    genres = random.sample(GENRES_LIST, 2)
    movies = get_movies_by_genre(genres)
    return genres, movies

def save_to_watchlist(title):
    if title not in WATCHLIST:
        WATCHLIST.append(title)
        return f"✅ '{title}' added to your watchlist."
    return f"⚠️ '{title}' is already in your watchlist."

def get_watchlist():
    return WATCHLIST

def chatbot_response(user_input):
    greetings = ["hi", "hello", "yo", "hii", "hey", "hola"]
    if user_input.lower().strip() in greetings:
        return "Hey! I'm your movie buddy 🍿. Tell me what you're in the mood for!", []

    genres = extract_genres(user_input)
    if not genres:
        genre_like = any(word in user_input.lower() for word in ["movie", "film", "genre", "watch", "suggest", "recommend", "try"])
        if not genre_like:
            return "🎭 I couldn’t identify any genres from that. Try again with a few keywords like 'horror comedy' or 'romantic drama'.", []
        else:
            prompt = f"Suggest some movies based on this request: {user_input}. Include a short narrative line for each."
            movie_blocks = get_movies_by_genre([user_input])
            return format_movie_list(movie_blocks), [m["title"] for m in movie_blocks]

    movie_blocks = get_movies_by_genre(genres)
    return format_movie_list(movie_blocks), [m["title"] for m in movie_blocks]

def delete_from_watchlist(titles):
    global WATCHLIST
    WATCHLIST = [title for title in WATCHLIST if title not in titles]



def format_movie_list(movie_list):
    enriched = []
    for movie in movie_list[:5]:
        details = fetch_tmdb_details(movie["title"])
        details["narrative"] = movie.get("narrative", "")
        enriched.append(details)

    if not enriched:
        return "⚠️ No matching genres found. Try again with different genres."

    result = "🎥 **Recommended Movies:**\n\n"
    for movie in enriched:
        result += f"🎬 **{movie['title']}**\n"
        result += f"   📊 Popularity: {movie['popularity']}\n"
        result += f"   📅 Release Date: {movie['release_date']}\n"
        result += f"   🌍 Language: {movie['language']}\n"
        result += f"   🇺🇸 Country: {movie['country']}\n"
        result += f"   🔄 Alternative Title: {movie['alt_title']}\n"
        if movie["narrative"]:
            result += f"   🎞️ A Sneak Peek: {movie['narrative']}\n"
        result += "\n"

    return result.strip()
watchlist = []

def add_to_watchlist(movies):
    added = []
    for m in movies:
        if m not in watchlist:
            watchlist.append(m)
            added.append(m)
    return added

def get_watchlist():
    return watchlist

def delete_from_watchlist(titles):
    global watchlist
    watchlist = [t for t in watchlist if t not in titles]

