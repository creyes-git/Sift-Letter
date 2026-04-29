"""
scraper.py – Fetches and parses news articles using Scrapling's StealthyFetcher.

StealthyFetcher launches a real Chromium-based browser with full anti-bot evasion
(realistic user-agent rotation, headless fingerprint spoofing, human-like timing)
so it works on sites that block simple HTTP requests.
"""

import logging
from urllib.parse import urljoin, urlparse

# StealthyFetcher is Scrapling's high-stealth browser-based fetcher.
# It uses Playwright under the hood with extensive fingerprint randomisation.
from scrapling.fetchers import StealthyFetcher

logger = logging.getLogger(__name__)

_JUNK_KEYWORDS = frozenset([
    "login", "subscribe", "newsletter", "about", "contact",
    "privacy", "terms", "policy", "author", "authors", "video", "podcasts",
    "tag", "category", "search", "feed", "rss", "sitemap",
])

_MIN_TITLE_LEN = 25


def _extract_domain(url: str) -> str:
    """Return the bare domain (e.g. 'techcrunch.com') from a full URL."""
    return urlparse(url).netloc.replace("www.", "")


def fetch_news(urls: list[str]) -> list[dict]:
    """
    Iterate over *urls*, fetch each page with StealthyFetcher, and extract
    article titles + links from the page.

    Args:
        urls: List of news-source URLs to scrape.

    Returns:
        A list of dicts with keys: 'title', 'link', 'source'.
    """
    articles: list[dict] = []
    seen_hrefs: set[str] = set()  # global dedup across all sources

    for url in urls:
        logger.info("Fetching: %s", url)
        try:
            # humanize=True adds realistic mouse movements and random delays
            # between actions, making the request pattern indistinguishable
            # from a real human browsing session.
            page = StealthyFetcher.fetch(url, humanize=True)
        except Exception as exc:
            logger.error("Failed to fetch %s: %s", url, exc)
            continue

        source = _extract_domain(url)

        # ── Extract anchor tags ───────────────────────────────────────────────
        # Scrapling returns an Adaptor object with a CSS/XPath selector API
        # similar to BeautifulSoup but built on lxml for speed.
        try:
            links = page.css("a")
        except Exception as exc:
            logger.error("Failed to parse %s: %s", url, exc)
            continue

        for anchor in links:
            # Grab the visible text content of the <a> tag
            title = anchor.text.strip() if anchor.text else ""

            # Scrapling anchors expose .attrib (dict-like) for HTML attributes
            href = anchor.attrib.get("href", "").strip()

            # Skip empty, javascript:void, anchors, or already-seen links
            if not title or not href or href.startswith(("#", "javascript:")):
                continue

            # Resolve relative URLs to absolute
            if not href.startswith(("http://", "https://")):
                href = urljoin(url, href)

            # Skip duplicates within this page
            if href in seen_hrefs:
                continue
            seen_hrefs.add(href)

            # Basic quality filter: skip very short titles (nav items, etc.)
            if len(title) < _MIN_TITLE_LEN:
                continue
                
            # Heuristic to filter out non-article links like "Log In", "About", "Contact"
            # Most news articles have longer paths, contain "article", "news", or date patterns
            path = urlparse(href).path.lower()
            is_likely_article = (
                "article" in path or 
                "news" in path or 
                "story" in path or 
                "market" in path or
                len(path.split("/")) > 3 or # Deeply nested paths are usually articles
                any(char.isdigit() for char in path) # Dates or IDs in path
            )
            
            is_junk = any(junk in path for junk in _JUNK_KEYWORDS)

            if is_junk or not is_likely_article:
                continue

            articles.append(
                {
                    "title": title,
                    "link": href,
                    "source": source,
                }
            )
            logger.debug("  Found: %s", title[:80])

    logger.info("Scraped %d raw articles from %d URL(s).", len(articles), len(urls))
    return articles
