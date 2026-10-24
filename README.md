# Kinotrailer Lübeck – wöchentliche Cloud-Aktualisierung

Die bestehende `index.html` bleibt eine statische Website. Ein geplanter GitHub Actions Workflow lädt montags das Lübecker Kinoprogramm von CINEMA.de, validiert die erkannten Daten und aktualisiert `data/kinoprogramm.json`. Die HTML-Seite lädt diese JSON-Datei beim Öffnen und baut die Filmliste dynamisch auf. Trailer öffnen eine YouTube-Suche zum Filmtitel.

## Einmalige Einrichtung

1. Melde dich bei GitHub an und erstelle ein **neues Repository** namens `kinotrailer-luebeck`.
2. Lade alle Dateien und Ordner aus diesem Paket in das Repository hoch. Wichtig: `.github/workflows/update-program.yml` muss mit hochgeladen werden. Falls GitHub versteckte Ordner nicht mit anzeigt, lade die ZIP über die Weboberfläche hoch oder nutze GitHub Desktop.
3. Öffne **Settings → Pages** und wähle **Deploy from a branch**, Branch `main`, Ordner `/(root)`, dann **Save**.
4. Öffne **Actions → Kinoprogramm aktualisieren → Run workflow**, um die erste Aktualisierung sofort anzustoßen.
5. Warte, bis der Workflow erfolgreich abgeschlossen ist. Öffne danach die veröffentlichte GitHub-Pages-Adresse, die unter **Settings → Pages** angezeigt wird.

## Aktualisierungsrhythmus

- Automatisch jeden Montag um 05:17 UTC (06:17 MEZ im Winter / 07:17 MESZ im Sommer).
- Bei einem neuen Commit und manuell über **Run workflow**.
- GitHub kann geplante Läufe bei hoher Auslastung verzögern. Die Website zeigt den Zeitstempel der zuletzt erfolgreich gespeicherten Daten.

## Zuverlässigkeit und Grenzen

- Die Aktualisierung bricht ab, wenn zu wenige Filme erkannt werden; dadurch wird die bestehende JSON-Datei nicht mit einer leeren Liste überschrieben.
- Die Datenquelle ist CINEMA.de: https://www.cinema.de/kino/kinoprogramm/luebeck. Falls die Seite ihre HTML-Struktur ändert oder automatisierte Abrufe blockiert, muss der Scraper angepasst werden. Nach der Einrichtung bitte den ersten Workflow-Lauf kontrollieren.
- Diese Lösung ist kostenlos nutzbar, solange die GitHub-Nutzungsbedingungen und Limits eingehalten werden. Sie benötigt ein GitHub-Konto und ein öffentliches oder passend konfiguriertes Repository.
- Die Vorschaubilder sind gestaltete Titelgrafiken, keine offiziellen Filmplakate. Spielzeiten können sich kurzfristig ändern; vor dem Kinobesuch beim Kino prüfen.
