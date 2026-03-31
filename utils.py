import json
import os
import logging

logger = logging.getLogger(__name__)

HISTORY_PATH = os.path.join(os.path.dirname(__file__), "history.json")

# Maps each provider name to the environment variable that holds its API key
_PROVIDER_KEY_ENV = {
    "gemini": "GEMINI_API_KEY",
    "claude": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "groq":   "GROQ_API_KEY",
}

def load_config() -> dict:
    """
    Load configuration directly from environment variables.
    This is designed to run seamlessly in GitHub Actions.
    """
    provider = os.environ.get("AI_PROVIDER", "gemini").lower()

    if provider not in _PROVIDER_KEY_ENV:
        raise ValueError(
            f"AI_PROVIDER '{provider}' is not supported. "
            f"Must be one of: {', '.join(_PROVIDER_KEY_ENV)}"
        )

    api_key_env = _PROVIDER_KEY_ENV[provider]

    cfg = {
        "urls": [url.strip() for url in os.environ.get("NEWS_SOURCES", "").split(",") if url.strip()],
        "topics": os.environ.get("INVESTMENT_FOCUS", ""),
        "subscriber_email": os.environ.get("SUBSCRIBER_EMAIL", ""),
        "ai_provider": provider,
        "ai_model": os.environ.get("AI_MODEL", "").strip(),  # Optional – falls back to provider default if empty or invalid
        "ai_api_key": os.environ.get(api_key_env, ""),
        "resend_api_key": os.environ.get("RESEND_API_KEY", ""),
    }

    # Build a human-readable list of missing env vars
    missing_env_vars = []
    if not cfg["urls"]:
        missing_env_vars.append("NEWS_SOURCES")
    if not cfg["topics"]:
        missing_env_vars.append("INVESTMENT_FOCUS")
    if not cfg["subscriber_email"]:
        missing_env_vars.append("SUBSCRIBER_EMAIL")
    if not cfg["ai_api_key"]:
        missing_env_vars.append(api_key_env)
    if not cfg["resend_api_key"]:
        missing_env_vars.append("RESEND_API_KEY")

    if missing_env_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_env_vars)}. "
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


_MAX_HISTORY_SIZE = 1000


def save_history(urls: list[str], path: str = HISTORY_PATH) -> None:
    """Save newly sent article URLs to history, capping at the most recent entries."""
    existing = load_history(path)
    updated = list(set(existing + urls))
    # Keep only the most recent entries to prevent unbounded growth
    if len(updated) > _MAX_HISTORY_SIZE:
        updated = updated[-_MAX_HISTORY_SIZE:]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(updated, f, indent=2)
