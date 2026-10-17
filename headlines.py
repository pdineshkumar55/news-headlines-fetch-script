"""
headlines.py - Print the top 5 headlines from BBC News.

Usage:
    pip install requests beautifulsoup4
    python headlines.py
"""

import sys

import requests
from bs4 import BeautifulSoup

URL = "https://www.bbc.com/news"

# Found by right-clicking a headline -> Inspect on bbc.com/news.
# Each headline is an <h2 data-testid="card-headline">.
# Verified in the browser console first with:
#   document.querySelectorAll('[data-testid="card-headline"]')
SELECTOR = '[data-testid="card-headline"]'

TOP_N = 5

# A normal browser User-Agent; some sites block the default "python-requests/x.y".
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0 Safari/537.36"
    ),
    "Accept-Language": "en-GB,en;q=0.9",
}


def fetch_page(url):
    """Return the page HTML, or None if the request fails or the status isn't 200."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
    except requests.RequestException as err:
        print(f"Error: could not reach {url}: {err}")
        return None

    if response.status_code != 200:
        print(f"Error: {url} returned HTTP {response.status_code}")
        return None

    return response.text


def extract_headlines(html, limit):
    """Return up to `limit` unique, non-empty headline strings."""
    soup = BeautifulSoup(html, "html.parser")
    headlines = []
    seen = set()

    for tag in soup.select(SELECTOR):
        # Strip ends and collapse any internal runs of whitespace/newlines.
        text = " ".join(tag.get_text().split())

        if not text:
            continue  # skip empty entries
        key = text.lower()
        if key in seen:
            continue  # skip duplicates (same story shown in two sections)

        seen.add(key)
        headlines.append(text)
        if len(headlines) == limit:
            break

    return headlines


def main():
    html = fetch_page(URL)
    if html is None:
        sys.exit(1)

    headlines = extract_headlines(html, TOP_N)

    if not headlines:
        print(
            "No headlines found. The selector may be out of date, "
            "or the page may be loading its headlines with JavaScript."
        )
        sys.exit(1)

    if len(headlines) < TOP_N:
        print(f"Warning: only found {len(headlines)} headline(s), expected {TOP_N}.\n")

    for number, headline in enumerate(headlines, start=1):
        print(f"{number}. {headline}")


if __name__ == "__main__":
    main()