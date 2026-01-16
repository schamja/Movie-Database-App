from storage import movie_storage_sql as storage


def command_generate_website():
    """Erstellt die index.html und füllt alle Platzhalter inklusive Statistiken."""
    movies = storage.list_movies()
    stats = storage.get_stats()  # Holt total, average, median, best, worst

    if not movies:
        print("Keine Filme zum Generieren vorhanden.")
        return

    # 1. Movie Grid HTML bauen
    movie_grid_html = ""
    for title, data in movies.items():
        poster_url = data['poster']
        if not poster_url or poster_url == "N/A":
            poster_url = ("https://images.unsplash.com/"
                          "photo-1594909122845-11baa439b7bf?q=80&w=300&h=450&auto=format&fit=crop")

        movie_html = f"""
        <div class="movie-card">
            <img src="{poster_url}" alt="Poster">
            <div class="card-body">
                <h3>{title}</h3>
                <div class="rating">{data['rating']}</div>
                <p style="color: #888; font-size: 0.9em;">{data['year']}</p>
            </div>
        </div>
        """
        movie_grid_html += movie_html

    try:
        # 2. Template laden
        with open("_static/index_template.html", "r", encoding="utf-8") as file:
            template_content = file.read()

        # 3. ALLE Platzhalter ersetzen
        final_html = template_content.replace("__TEMPLATE_TITLE__", "Meine Movie App")
        final_html = final_html.replace("__TEMPLATE_MOVIE_GRID__", movie_grid_html)

        # Statistiken einfügen (Wichtig: Werte in Strings umwandeln!)
        final_html = final_html.replace("__TOTAL_MOVIES__", str(stats['total']))
        final_html = final_html.replace("__AVG_RATING__", str(stats['average']))
        final_html = final_html.replace("__MEDIAN_RATING__", str(stats['median']))

        # 4. In index.html speichern
        with open("index.html", "w", encoding="utf-8") as file:
            file.write(final_html)

        print("✨ Website wurde erfolgreich aktualisiert!")
    except Exception as e:
        print(f"Fehler beim Generieren: {e}")


def command_statistics():
    s = storage.get_stats()
    if s["total"] == 0:
        return print("Keine Filme.")

    print("\n--- STATISTIKEN ---")
    print(f"Filme: {s['total']} | Schnitt: {s['average']} | Median: {s['median']}")
    print(f"Bester: {s['best'][0]} ({s['best'][1]})")
    print(f"Schlechtester: {s['worst'][0]} ({s['worst'][1]})")


def main():
    # Hier wird die Funktion aufgerufen, die vorher den Fehler verursacht hat


    while True:
        print("\n--- MOVIE APP MENU ---")
        print("1. Filme auflisten")
        print("2. Filme Einfügen")
        print("3. Film löschen")
        print("4. Film aktualisieren")
        print("5. Statistiken")
        print("6. Film suchen")
        print("7. Sortieren nach Rating")
        print("8. Zufallsfilm") # NEU
        print("9. Webseite generieren")
        print("0. Beenden")

        choice = input("\n Wähle eine Option: ")

        if choice == "1":
            movies = storage.list_movies()
            for title, data in movies.items():
                print(f"🎬 {title} - {data['rating']} ({data['year']})")

        elif choice == "2":
            title = input("Film-Titel eingeben: ")
            storage.add_movie_via_api(title)

        elif choice == "3":
            title = input("Welchen Film löschen? ")
            # 1. Löschen in der Datenbank und Ergebnis prüfen
            # Wir nutzen den Rückgabewert (True/False) deiner storage.delete_movie Funktion
            if storage.delete_movie(title):
                print(f"Der Film '{title}' wurde erfolgreich aus der DB gelöscht.")

                # 2. Webseite sofort neu generieren
                command_generate_website()
                print("Die Webseite wurde automatisch aktualisiert.")
            else:
                # Falls rowcount 0 war (Film nicht gefunden)
                print(f"Fehler: Der Film '{title}' wurde in der Datenbank nicht gefunden.")

        elif choice == "4":
            title = input("Welchen Film möchtest du aktualisieren? ")
            try:
                new_rating = float(input("Gib das neue Rating ein (z.B. 8.5): "))

                # 1. Update in der Datenbank
                if storage.update_movie(title, new_rating):
                    print(f" Rating für '{title}' wurde aktualisiert.")

                    # 2. WICHTIG: Webseite sofort neu bauen!
                    command_generate_website()
                    print(" Webseite wurde mit dem neuen Rating aktualisiert.")
                else:
                    print(f" Fehler: Film '{title}' wurde nicht gefunden.")

            except ValueError:
                print(" Bitte gib eine gültige Zahl für das Rating ein.")

        elif choice == "6":
            term = input("Suche nach Anfangsbuchstabe der TITLE DES FILMS: ")
            results = storage.search_movies(term)
            if results:
                # Optional: Anzahl der Treffer anzeigen
                print(f"\nEs wurden {len(results)} Filme gefunden:")
                for row in results:
                    print(f" 🎬 {row[0]} ({row[1]}) - Rating: {row[2]}")
            else:
                print(f"Keine passenden Filme für '{term}' gefunden.")

        elif choice == "7":
            # WICHTIG: Hier muss das Argument True übergeben werden!
            movies = storage.list_movies(sort_by_rating=True)
            print("\n--- FILME NACH BEWERTUNG (Beste zuerst) ---")
            for title, data in movies.items():
                print(f"⭐ {data['rating']} | {title}")

        elif choice == "8":
            result = storage.get_random_movie()
            if result:
                title, data = result
                print(f"Zufallsfilm: {title} ({data['year']}) - Bewertung: {data['rating']}")
            else:
                print("Keine Filme gefunden.")

        elif choice == "9":
            command_generate_website()

        elif choice == "0":
            break

if __name__ == "__main__":
    main()