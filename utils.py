import json
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

HISTORY_PATH = os.path.join(os.path.dirname(__file__), "history.json")

def load_config() -> dict:
    """
    Load configuration directly from environment variables.
    This is designed to run seamlessly in GitHub Actions.
    """
    cfg = {
        "urls": [url.strip() for url in os.environ.get("NEWS_SOURCES", "").split(",") if url.strip()],
        "topics": os.environ.get("INVESTMENT_FOCUS", ""),
        "subscriber_email": os.environ.get("SUBSCRIBER_EMAIL", ""),
        "gemini_api_key": os.environ.get("GEMINI_API_KEY", ""),
        "resend_api_key": os.environ.get("RESEND_API_KEY", "")
    }

    required_keys = ("urls", "topics", "subscriber_email", "gemini_api_key", "resend_api_key")
    missing = [k for k in required_keys if not cfg.get(k)]
    
    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}. "
            "Please configure these in your GitHub Repository Secrets and Variables."
        )

    return cfg

def load_history(path: str = HISTORY_PATH) -> list[str]:
    """Load previously sent article URLs to avoid duplicates."""
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def save_history(urls: list[str], path: str = HISTORY_PATH) -> None:
    """Save newly sent article URLs to history."""
    existing = load_history(path)
    # Use a set to maintain uniqueness, then list
    updated = list(set(existing + urls))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(updated, f, indent=2)
