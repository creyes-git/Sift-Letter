"""
main.py – Orchestrator for the AI Finance Newsletter pipeline.
"""

import logging
import sys

from modules.ai_processor import curate_news
from modules.delivery import send_newsletter
from modules.market_data import fetch_market_snapshot
from modules.scraper import fetch_news
from modules.utils import load_config, load_history, save_history

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

def run() -> None:
    """Execute the full newsletter pipeline."""
    logger.info("=" * 60)
    logger.info("  AI Finance Newsletter Pipeline – Starting")
    logger.info("=" * 60)

    # ── Step 1: Load configuration ─────────────────────────────────────────
    logger.info("Step 1/5 – Loading configuration…")
    try:
        config = load_config()
    except (FileNotFoundError, ValueError) as exc:
        logger.error("Configuration error: %s", exc)
        logger.error("Aborting pipeline.")
        sys.exit(1)

    # ── Step 2: Fetch Market Data ──────────────────────────────────────────
    logger.info("Step 2/5 – Fetching Market Snapshot…")
    try:
        market_data = fetch_market_snapshot()
    except Exception as exc:
        logger.error("Market data fetching failed: %s", exc)
        market_data = {}

    # ── Step 3: Scrape news ────────────────────────────────────────────────
    logger.info("Step 3/5 – Scraping news from %d source(s)…", len(config["urls"]))
    try:
        raw_articles = fetch_news(config["urls"])
        if not raw_articles:
            logger.warning("No articles scraped. The sources may be empty or blocked.")
    except Exception as exc:
        logger.error("Scraping failed: %s", exc, exc_info=True)
        sys.exit(1)

    # ── Step 3.5: Filter History ───────────────────────────────────────────
    sent_urls = set(load_history())
    if sent_urls and raw_articles:
        original_count = len(raw_articles)
        raw_articles = [a for a in raw_articles if a.get("link") not in sent_urls]
        logger.info("Filtered out %d already-sent articles. %d remaining.", original_count - len(raw_articles), len(raw_articles))

    if not raw_articles:
        logger.warning("No new articles to process. Exiting.")
        sys.exit(0)

    # ── Step 4: AI curation ────────────────────────────────────────────────
    logger.info("Step 4/5 – Curating articles with %s…", config["ai_provider"])
    try:
        curated_data = curate_news(raw_articles, config, market_data)
    except Exception as exc:
        logger.error("AI curation failed: %s", exc, exc_info=True)
        sys.exit(1)

    # ── Step 5: Send email ─────────────────────────────────────────────────
    logger.info("Step 5/5 – Sending newsletter to %s…", config["subscriber_email"])
    try:
        send_newsletter(curated_data, market_data, config)
    except Exception as exc:
        logger.error("Email delivery failed: %s", exc, exc_info=True)
        sys.exit(1)

    # History save is intentionally outside the delivery try-block so a disk/IO
    # failure here is not reported as an email failure (the email already went out).
    processed_urls = [art["link"] for art in raw_articles if art.get("link")]
    if processed_urls:
        try:
            save_history(processed_urls)
            logger.info("Saved %d article URLs to history.", len(processed_urls))
        except Exception as exc:
            logger.error("Failed to update history (email was sent): %s", exc, exc_info=True)

    logger.info("=" * 60)
    logger.info("  Newsletter delivered successfully! 🎉")
    logger.info("=" * 60)

if __name__ == "__main__":
    run()
