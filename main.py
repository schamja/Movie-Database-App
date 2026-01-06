from storage import movie_storage_sql as storage
import sys

def command_generate_website():
    """Erstellt die index.html basierend auf dem Design-Template."""
    movies = storage.list_movies()
    if not movies:
        print("Keine Filme zum Generieren vorhanden.")
        return

    movie_grid_html = ""
    for title, data in movies.items():
        # 1. Fallback Bild Logik
        poster_url = data['poster']
        if not poster_url or poster_url == "N/A":
            poster_url = "https://images.unsplash.com/photo-1594909122845-11baa439b7bf?q=80&w=300&h=450&auto=format&fit=crop"

        # 2. Trailer-Link generieren
        search_query = f"{title} {data['year']} official trailer".replace(" ", "+")
        trailer_url = f"https://www.youtube.com/results?search_query={search_query}"

        # 3. HTML Block bauen (nur einmal!)
        movie_html = f"""
        <div class="movie-card">
            <img src="{poster_url}" alt="Poster">
            <div class="card-body">
                <h3>{title}</h3>
                <div class="rating">{data['rating']}</div>
                <p style="color: #888; font-size: 0.9em;">{data['year']}</p>
                <br>
                <a href="{trailer_url}" target="_blank" class="trailer-button">Trailer anschauen</a>
            </div>
        </div>
        """
        # 4. Zum Grid hinzufügen
        movie_grid_html += movie_html

    try:
        with open("_static/index_template.html", "r", encoding="utf-8") as file:
            template_content = file.read()

        final_html = template_content.replace("__TEMPLATE_TITLE__", "Meine Movie App")
        final_html = final_html.replace("__TEMPLATE_MOVIE_GRID__", movie_grid_html)

        with open("index.html", "w", encoding="utf-8") as file:
            file.write(final_html)

        print("✨ Website wurde erfolgreich mit Trailer-Links generiert!")
    except Exception as e:
        print(f"Fehler beim Generieren: {e}")

def command_statistics():
    """Zeigt die Film-Statistiken an."""
    stats = storage.get_stats()
    if stats["total"] == 0:
        print("Keine Daten für Statistiken verfügbar.")
        return

    print("\n--- FILM STATISTIKEN ---")
    print(f"Gesamtanzahl der Filme: {stats['total']}")
    print(f"Durchschnittliche Bewertung: ⭐ {stats['average']}")
    print(f"Spitzenreiter: {stats['best_movie']} (Rating: {stats['best_rating']})")
    print("--------------------------")

def main():
    while True:
        print("\n--- MOVIE DATABASE MENU ---")
        print("1. Filme auflisten")
        print("2. Film hinzufügen (API)")
        print("3. Film löschen")
        print("5. Statistiken anzeigen")
        print("9. Webseite generieren")
        print("0. Beenden")

        choice = input("\nWähle eine Option: ")

        if choice == "1":
            movies = storage.list_movies()
            for title, data in movies.items():
                print(f"🎬 {title} - {data['rating']} ({data['year']})")
        elif choice == "2":
            title = input("Film-Titel eingeben: ")
            storage.add_movie_via_api(title)
        elif choice == "3":
            title = input("Welchen Film löschen? ")
            storage.delete_movie(title)
        elif choice == "5":
            command_statistics()
        elif choice == "9":
            command_generate_website()
        elif choice == "0":
            print("Bye!")
            sys.exit()
        else:
            print("Ungültige Wahl.")

if __name__ == "__main__":
    main()