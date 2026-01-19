import storage.movie_storage_sql as storage


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


def command_list_movies():
    """Listet alle Filme aus der Datenbank auf."""
    movies = storage.list_movies()
    if not movies:
        print("Die Datenbank ist leer.")
        return
    for title, data in movies.items():
        print(f"🎬 {title} - {data['rating']} ({data['year']})")

def command_add_movie():
    """Fragt nach einem Titel und fügt den Film via API hinzu."""
    title = input("Film-Titel eingeben: ")
    if storage.add_movie_via_api(title):
        print(f"✅ '{title}' wurde erfolgreich hinzugefügt.")
        command_generate_website()
    else:
        print(f"❌ Fehler: Film '{title}' konnte nicht gefunden werden.")

def command_delete_movie():
    """Löscht einen Film nach Benutzereingabe."""
    title = input("Welchen Film möchtest du löschen? ")
    if storage.delete_movie(title):
        print(f"✅ '{title}' wurde gelöscht.")
        command_generate_website()
    else:
        print(f"❌ Fehler: Film '{title}' nicht gefunden.")

def command_update_movie():
    """Modularisierte Option 4: Aktualisiert das Rating eines Films."""
    title = input("Welchen Film möchtest du aktualisieren? ")
    try:
        new_rating = float(input("Gib das neue Rating ein (z.B. 8.5): "))
        if storage.update_movie(title, new_rating):
            print(f"✅ Rating für '{title}' wurde aktualisiert.")
            command_generate_website()
        else:
            print(f"❌ Fehler: Film '{title}' wurde nicht gefunden.")
    except ValueError:
        print("⚠ Bitte gib eine gültige Zahl ein.")

def command_statistics():
    """Modularisierte Option 5: Zeigt Film-Statistiken an."""
    s = storage.get_stats()
    if s["total"] == 0:
        print("Keine Filme für Statistiken vorhanden.")
        return
    print("\n--- STATISTIKEN ---")
    print(f"Filme: {s['total']} | Schnitt: {s['average']} | Median: {s['median']}")
    print(f"Bester: {s['best'][0]} ({s['best'][1]})")
    print(f"Schlechtester: {s['worst'][0]} ({s['worst'][1]})")

def command_search_movies():
    """Modularisierte Option 6: Sucht Filme nach Titeln."""
    term = input("Suche nach dem Titel des Films: ")
    results = storage.search_movies(term)
    if results:
        print(f"\nGefundene Filme ({len(results)}):")
        for row in results:
            print(f" 🎬 {row[0]} ({row[1]}) - Rating: {row[2]}")
    else:
        print(f"Keine Treffer für '{term}'.")

def command_sort_by_rating():
    """Modularisierte Option 7: Sortiert Filme nach Bewertung."""
    movies = storage.list_movies(sort_by_rating=True)
    print("\n--- FILME NACH BEWERTUNG (Beste zuerst) ---")
    for title, data in movies.items():
        print(f"⭐ {data['rating']} | {title}")

def command_random_movie():
    """Modularisierte Option 8: Zeigt einen Zufallsfilm an."""
    result = storage.get_random_movie()
    if result:
        title, data = result
        print(f"🎲 Zufallsempfehlung: {title} ({data['year']}) - Rating: {data['rating']}")
    else:
        print("Datenbank ist leer.")



def main():
    """Hauptmenü-Schleife der App."""
    while True:
        print("\n--- MOVIE APP MENU ---")
        print("1. Filme auflisten\n2. Film hinzufügen\n3. Film löschen")
        print("4. Film aktualisieren\n5. Statistiken\n6. Film suchen")
        print("7. Sortieren nach Rating\n8. Zufallsfilm\n9. Webseite generieren\n0. Beenden")

        choice = input("\nWähle eine Option: ")

        if choice == "1": command_list_movies()
        elif choice == "2": command_add_movie()
        elif choice == "3": command_delete_movie()
        elif choice == "4": command_update_movie()
        elif choice == "5": command_statistics()
        elif choice == "6": command_search_movies()
        elif choice == "7": command_sort_by_rating()
        elif choice == "8": command_random_movie()
        elif choice == "9": command_generate_website()
        elif choice == "0": break
        else: print("Ungültige Eingabe.")

if __name__ == "__main__":
    main()