#!/usr/bin/env python3
"""Fetches the Lübeck cinema listing and writes data/kinoprogramm.json.
The source is CINEMA.de; the HTML structure may change, so the workflow keeps
an existing data file if parsing fails rather than publishing an empty list.
"""
from __future__ import annotations
import json, re, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from html import unescape
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data' / 'kinoprogramm.json'
URL = 'https://www.cinema.de/kino/kinoprogramm/luebeck'
TIME_RE = re.compile(r'(?<!\d)(?:[01]?\d|2[0-3]):[0-5]\d(?!\d)')

def clean(s: str) -> str:
    return re.sub(r'\s+', ' ', unescape(s)).strip(' \t\r\n•·-')

def extract(soup: BeautifulSoup) -> list[dict]:
    films: dict[str, dict] = {}
    # Preferred path: table rows where film title and showtime occur together.
    for tr in soup.select('tr'):
        cells = [clean(x.get_text(' ', strip=True)) for x in tr.select('th,td')]
        if len(cells) < 2:
            continue
        joined = ' '.join(cells)
        times = sorted(set(TIME_RE.findall(joined)))
        if not times:
            continue
        links = [clean(a.get_text(' ', strip=True)) for a in tr.select('a')]
        candidates = [x for x in (links + cells) if x and not TIME_RE.fullmatch(x) and not re.search(r'Kinoprogramm|Bewertung|Uhrzeit|Kino$', x, re.I)]
        title = next((x for x in candidates if len(x) > 2 and not re.fullmatch(r'\d+(?:[,.]\d+)?', x)), None)
        if title:
            films.setdefault(title, {'title': title, 'showtimes': [], 'cinemas': []})
            films[title]['showtimes'] = sorted(set(films[title]['showtimes'] + times))
            cinema = next((x for x in cells if re.search(r'CineStar|Filmhaus|Koki|Kommunales Kino', x, re.I)), None)
            if cinema and cinema not in films[title]['cinemas']:
                films[title]['cinemas'].append(cinema)

    # Fallback for list/card markup: use JSON-LD Event records if available.
    if not films:
        for script in soup.select('script[type="application/ld+json"]'):
            try:
                data = json.loads(script.string or script.get_text())
            except Exception:
                continue
            stack = data if isinstance(data, list) else [data]
            while stack:
                item = stack.pop()
                if isinstance(item, dict):
                    if isinstance(item.get('@graph'), list): stack.extend(item['@graph'])
                    if isinstance(item.get('itemListElement'), list): stack.extend(item['itemListElement'])
                    name = clean(str(item.get('name', '')))
                    if name and item.get('@type') in ('Movie', 'Event', 'ScreeningEvent'):
                        films.setdefault(name, {'title': name, 'showtimes': [], 'cinemas': []})
                elif isinstance(item, list): stack.extend(item)

    # Last fallback: extract movie-title/time rows from rendered text, avoiding an empty overwrite.
    if not films:
        lines = [clean(x) for x in soup.get_text('\n').splitlines()]
        lines = [x for x in lines if x]
        for i, line in enumerate(lines):
            times = TIME_RE.findall(line)
            if times:
                title = clean(TIME_RE.sub('', line))
                if len(title) > 2 and not re.search(r'Kinoprogramm|Uhrzeit|Bewertung', title, re.I):
                    films.setdefault(title, {'title': title, 'showtimes': [], 'cinemas': []})
                    films[title]['showtimes'] = sorted(set(films[title]['showtimes'] + times))
    return sorted(films.values(), key=lambda x: x['title'].casefold())

def main() -> None:
    req = Request(URL, headers={'User-Agent': 'Mozilla/5.0 (compatible; LuebeckKinoProgramm/1.0; +https://github.com/)','Accept-Language':'de-DE,de;q=0.9'})
    with urlopen(req, timeout=30) as response:
        html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    movies = extract(soup)
    if len(movies) < 5:
        raise RuntimeError(f'Zu wenige Filme erkannt ({len(movies)}); vorhandene Daten bleiben erhalten.')
    payload = {
        'source': URL,
        'city': 'Lübeck',
        'updatedAt': datetime.now(timezone.utc).isoformat(),
        'count': len(movies),
        'movies': movies,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'{len(movies)} Filme gespeichert: {OUT}')

if __name__ == '__main__':
    try: main()
    except Exception as exc:
        print(f'FEHLER: {exc}', file=sys.stderr)
        sys.exit(1)
