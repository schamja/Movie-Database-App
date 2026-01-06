import requests
import os
from sqlalchemy import create_engine, text

# 1. Definiere den Pfad zum data-Ordner
DB_FOLDER = "data"
DB_NAME = "movies.db"

# Erstelle den Pfad: 'data/movies.db'
# os.path.join sorgt für die richtigen Schrägstriche je nach Betriebssystem
DB_PATH = os.path.join(DB_FOLDER, DB_NAME)

# 2. Stelle sicher, dass der Ordner existiert (falls er mal gelöscht wird)
if not os.path.exists(DB_FOLDER):
    os.makedirs(DB_FOLDER)

# 3. SQLite URL mit dem neuen Pfad (relativ zum Hauptverzeichnis)
DB_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(DB_URL)

# WICHTIG: Nutze hier deinen aktivierten API-Key!
API_KEY = "dd74a077"
engine = create_engine(DB_URL)

# Datenbank beim Start initialisieren
with engine.connect() as connection:
    connection.execute(text("""
                            CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            year INTEGER NOT NULL,
            rating REAL NOT NULL,
            poster_url TEXT  -- <--- Diese Zeile wird JETZT erst wirklich ausgeführt!
        )
                            """))
    connection.commit()


def add_movie_via_api(title):
    """Sucht Film in API und speichert ihn in der DB."""
    url = f"http://www.omdbapi.com/?apikey={API_KEY}&t={title}"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()

        if data.get("Response") == "False":
            print(f"Fehler: {data.get('Error')}")
            return False

        extracted_data = {
            "title": data.get("Title"),
            "year": int(data.get("Year")[:4]) if data.get("Year") else 0,
            "rating": float(data.get("imdbRating")) if data.get("imdbRating") != "N/A" else 0.0,
            "poster": data.get("Poster")
        }

        with engine.connect() as connection:
            connection.execute(text("""
                INSERT OR REPLACE INTO movies (title, year, rating, poster_url)
                VALUES (:title, :year, :rating, :poster)
            """), extracted_data)
            connection.commit()

        print(f"✅ '{extracted_data['title']}' hinzugefügt!")
        return True
    except Exception as e:
        print(f" API-Fehler: {e}")
        return False


def list_movies():
    """Gibt alle Filme sortiert nach Bewertung (beste zuerst) zurück."""
    with engine.connect() as connection:
        result = connection.execute(text("SELECT title, year, rating, poster_url FROM movies ORDER BY rating DESC"))
        rows = result.fetchall()

    # Rückgabe als Dictionary für main.py
    return {row[0]: {"year": row[1], "rating": row[2], "poster": row[3]} for row in rows}


def delete_movie(title):
    """Löscht einen Film aus der Datenbank."""
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM movies WHERE title = :title"), {"title": title})
        connection.commit()
        print(f"🗑️ Movie '{title}' gelöscht.")

def get_stats():
    """Berechnet Statistiken direkt in der Datenbank."""
    with engine.connect() as connection:
        # 1. Durchschnittsbewertung
        avg_res = connection.execute(text("SELECT AVG(rating) FROM movies")).fetchone()
        # 2. Bester Film
        best_res = connection.execute(text("SELECT title, rating FROM movies ORDER BY rating DESC LIMIT 1")).fetchone()
        # 3. Anzahl der Filme
        count_res = connection.execute(text("SELECT COUNT(*) FROM movies")).fetchone()

    return {
        "average": round(avg_res[0], 2) if avg_res[0] else 0,
        "best_movie": best_res[0] if best_res else "N/A",
        "best_rating": best_res[1] if best_res else 0,
        "total": count_res[0]
    }