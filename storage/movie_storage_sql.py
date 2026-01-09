import os
import statistics
import requests
from sqlalchemy import create_engine, text

# SICHERHEIT: API Key aus Umgebungsvariable
API_KEY = os.getenv("OMDB_API_KEY", "dd74a077")
DB_PATH = os.path.join("data", "movies.db")
engine = create_engine(f"sqlite:///{DB_PATH}")


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

        print(f"'{extracted_data['title']}' erfolgreich hinzugefügt!")
        return True
    except Exception as e:
        print(f" API-Fehler: {e}")
        return False


def get_stats():
    """Berechnet Statistiken inkl. Median und Worst Movie."""
    with engine.connect() as connection:
        res = connection.execute(text("SELECT title, rating FROM movies ORDER BY rating ASC")).fetchall()

    if not res:
        return None

    ratings = [row[1] for row in res]
    return {
        "total": len(ratings),
        "average": round(statistics.mean(ratings), 2),
        "median": round(statistics.median(ratings), 2),
        "best_movie": res[-1][0],
        "best_rating": res[-1][1],
        "worst_movie": res[0][0],
        "worst_rating": res[0][1]
    }


# Stelle sicher, dass auch update_movie, search_movies und delete_movie hier stehen!

def delete_movie(title):
    try:
        with engine.connect() as connection:
            # .begin() startet eine Transaktion und macht das commit() automatisch
            with connection.begin():
                result = connection.execute(
                    text("DELETE FROM movies WHERE title = :t"),
                    {"t": title}
                )
                count = result.rowcount
                return count > 0
    except exc.SQLAlchemyError as e:
        print(f"SQL-Fehler aufgetreten: {e}")
        return False

def update_movie(title, rating):
    with engine.connect() as connection:
        result = connection.execute(text("UPDATE movies SET rating = :r WHERE title = :t"),
                                    {"r": rating, "t": title})
        connection.commit()
        return result.rowcount > 0

def get_stats():
    with engine.connect() as connection:
        res = connection.execute(text("SELECT title, rating FROM movies "
                                      "ORDER BY rating ASC")).fetchall()
    if not res: return None
    ratings = [row[1] for row in res]
    return {
        "total": len(ratings),
        "average": round(statistics.mean(ratings), 2),
        "median": round(statistics.median(ratings), 2),
        "best_movie": res[-1][0], "best_rating": res[-1][1],
        "worst_movie": res[0][0], "worst_rating": res[0][1]
    }

# Sicherere Variante für alle Datenbanken:
def search_movies(term):
    with engine.connect() as connection:
        return connection.execute(
            text("SELECT title, year, rating FROM movies WHERE LOWER(title) LIKE LOWER(:t)"),
            {"t": f"{term}%"} # Beidseitig % findet alles, was den Begriff enthält
        ).fetchall()


def list_movies(sort_by_rating=False):
    # CAST sorgt dafür, dass 9.1 wirklich größer als 9.0 ist
    order = "CAST(rating AS FLOAT) DESC" if sort_by_rating else "title ASC"

    with engine.connect() as connection:
        # Wir nutzen f-string nur für den ORDER-Teil (da Spaltennamen nicht als Parameter gehen)
        result = connection.execute(text(f"SELECT title, year, rating, poster_url FROM movies "
                                         f"ORDER BY {order}"))

        # Wir geben eine Liste von Dicts oder ein OrderedDict zurück,
        # um die Reihenfolge sicher zu erhalten
        return {row[0]: {"year": row[1], "rating": row[2], "poster": row[3]} for row in result}