import os
import requests
import statistics
import random
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# 1. SECURITY: Lädt den API-Key aus der .env Datei
load_dotenv()
API_KEY = os.getenv("OMDB_API_KEY")

# Datenbank-Setup
DB_PATH = os.path.join("data", "movies.db")
engine = create_engine(f"sqlite:///{DB_PATH}")


def list_movies(sort_by_rating=False):
    """Gibt alle Filme als Dictionary zurück."""
    order = "CAST(rating AS FLOAT) DESC" if sort_by_rating else "title ASC"

    try:
        with engine.connect() as connection:
            result = connection.execute(text(f"SELECT title, year, rating, poster_url FROM movies ORDER BY {order}"))
            return {row[0]: {"year": row[1], "rating": row[2], "poster": row[3]} for row in result}
    except Exception as e:
        print(f"Fehler beim Auflisten: {e}")
        return {}


def add_movie_via_api(title):
    """Fügt Film via OMDb API hinzu."""
    if not API_KEY:
        print("Fehler: Kein API_KEY in .env gefunden!")
        return False
    url = f"http://www.omdbapi.com/?apikey={API_KEY}&t={title}"
    try:
        data = requests.get(url).json()
        if data.get("Response") == "False":
            print(f"API Fehler: {data.get('Error')}")
            return False

        movie_data = {
            "t": data.get("Title"),
            "y": int(data.get("Year")[:4]) if data.get("Year") else 0,
            "r": float(data.get("imdbRating")) if data.get("imdbRating") != "N/A" else 0.0,
            "p": data.get("Poster")
        }
        with engine.connect() as connection:
            with connection.begin():
                connection.execute(text("""
                    INSERT OR REPLACE INTO movies (title, year, rating, poster_url)
                    VALUES (:t, :y, :r, :p)
                """), movie_data)
        return True
    except Exception as e:
        print(f"Fehler: {e}")
        return False


def delete_movie(title):
    """Löscht einen Film."""
    with engine.connect() as connection:
        with connection.begin():
            result = connection.execute(text("DELETE FROM movies WHERE title = :t"), {"t": title})
            return result.rowcount > 0


def update_movie(title, rating):
    """AKTUALISIERT das Rating eines Films (Behebt deinen Fehler)."""

    with engine.connect() as connection:
        with connection.begin():
            result = connection.execute(text("UPDATE movies SET rating = :r WHERE title = :t"),
                                        {"r": rating, "t": title})
            return result.rowcount > 0


def get_stats():
    """Berechnet Statistiken."""
    with engine.connect() as connection:
        res = connection.execute(text("SELECT title, rating FROM movies ORDER BY rating ASC")).fetchall()
    if not res:
        return {"total": 0, "average": 0, "median": 0, "best": ["N/A", 0], "worst": ["N/A", 0]}

    ratings = [row[1] for row in res]
    return {
        "total": len(ratings),
        "average": round(statistics.mean(ratings), 2),
        "median": round(statistics.median(ratings), 2),
        "best": [res[-1][0], res[-1][1]],
        "worst": [res[0][0], res[0][1]]
    }


# Sicherere Variante für alle Datenbanken:
def search_movies(term):
    with engine.connect() as connection:
        return connection.execute(
            text("SELECT title, year, rating FROM movies WHERE LOWER(title) LIKE LOWER(:t)"),
            {"t": f"{term}%"} # Beidseitig % findet alles, was den Begriff enthält
        ).fetchall()


def get_random_movie():
    """RANDOM FEATURE: Wählt zufälligen Film (Anforderung Tutorin)."""
    movies = list_movies()
    if not movies:
        return None

    t = random.choice(list(movies.keys()))
    return t, movies[t]