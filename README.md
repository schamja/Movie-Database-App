# 🎬 Movie Database App

Eine interaktive Python-Anwendung zur Verwaltung einer persönlichen Filmsammlung. 
Die App nutzt die **OMDb API**, um Filmdetails automatisch abzurufen, speichert diese 
in einer **SQLite-Datenbank** und generiert eine schicke **Web-Galerie**.

## 🚀 Features
- **API-Integration:** Automatische Suche nach Titeln, Erscheinungsjahren, Ratings und Postern.
- **Datenbank-Speicherung:** Dauerhafte Speicherung in SQLite (keine JSON-Dateien mehr nötig).
- **Statistiken:** Berechnet Durchschnittsbewertungen und findet den am besten bewerteten Film.
- **Web-Generator:** Erstellt per Knopfdruck eine `index.html` mit einem modernen Film-Grid.
- **Saubere Struktur:** Professionelle Aufteilung in Pakete (`storage/`) und Datenordner.

## 🛠️ Installation & Setup

1. **Repository klonen oder Dateien kopieren.**
2. **Virtuelle Umgebung erstellen (optional aber empfohlen):**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Unter Windows: .venv\Scripts\activate