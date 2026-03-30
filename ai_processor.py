"""
ai_processor.py – Uses an AI provider to deduplicate, rank, categorize, and summarize news.

Supported providers (configured via the AI_PROVIDER environment variable):
  - gemini  → Google Gemini 1.5 Flash
  - claude  → Anthropic Claude Haiku
  - openai  → OpenAI GPT-4o Mini
  - groq    → Groq Llama 3 70B
"""

import json
import logging
import re

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert financial analyst, portfolio manager, and market commentator.
Your task is to process a raw list of news article titles and links, alongside the user's investment focus and a snapshot of current market data, and produce a highly professional, curated daily market digest."""

USER_PROMPT_TEMPLATE = """Below is a snapshot of the current market indices, followed by a raw list of news articles scraped from various financial sources.
The user's investment focus / portfolio is: {topics}.

MARKET SNAPSHOT:
{market_data}

RAW ARTICLES:
{articles_block}

Your task – follow these steps exactly:
1. FILTER: Keep only articles relevant to the market broadly or the user's investment focus specifically. Discard unrelated or low-quality articles.
2. DEDUPLICATE: Remove articles that cover the exact same story. Keep the best representative.
3. RANK & CATEGORIZE: Assign each remaining article to one of these categories: "Macro & Economy", "Corporate Earnings & Movers", "Regulatory & Geopolitics", or "Crypto & Alternative". Assign an impact_score (1-10).
4. SUMMARIZE ARTICLES: Write a concise, insightful 2-sentence financial summary for each article. Explain *why* it matters to the market or the user's portfolio.
5. MARKET SUMMARY: Write a cohesive, engaging 1-paragraph summary of the overall market sentiment today based on the articles and market snapshot.
6. SENTIMENT SCORE: Determine an overall market sentiment: "Bullish", "Bearish", or "Neutral".

OUTPUT FORMAT — CRITICAL:
Return ONLY a valid JSON object. Do NOT wrap it in markdown code fences (no ```json).
The JSON object must have exactly this structure:
{{
  "market_sentiment": "Bullish" | "Bearish" | "Neutral",
  "market_summary": "Your 1-paragraph overview of today's market...",
  "categories": {{
    "Macro & Economy": [
      {{"title": "Example", "summary": "...", "link": "https...", "impact_score": 8}}
    ],
    "Corporate Earnings & Movers": [],
    "Regulatory & Geopolitics": [],
    "Crypto & Alternative": []
  }}
}}
"""


def _build_articles_block(raw_articles: list[dict]) -> str:
    lines = []
    for i, art in enumerate(raw_articles, start=1):
        lines.append(f"{i}. TITLE: {art['title']}\n   LINK:  {art['link']}")
    return "\n".join(lines)


def _safe_parse_json(raw_text: str) -> dict:
    text = raw_text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        logger.error("JSON parse error: %s\nRaw text snippet: %.300s", exc, text)
        raise ValueError(f"LLM returned invalid JSON: {exc}") from exc

    if not isinstance(parsed, dict) or "categories" not in parsed:
        raise ValueError(f"Expected a structured JSON object, got {type(parsed).__name__}")

    return parsed


def _curate_with_gemini(user_prompt: str, api_key: str) -> str:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=SYSTEM_PROMPT,
    )
    response = model.generate_content(
        user_prompt,
        generation_config=genai.GenerationConfig(
            temperature=0.2,
            response_mime_type="application/json",
        ),
    )
    return response.text


def _curate_with_claude(user_prompt: str, api_key: str) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4096,
        temperature=0.2,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return response.content[0].text


def _curate_with_openai(user_prompt: str, api_key: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content


def _curate_with_groq(user_prompt: str, api_key: str) -> str:
    from groq import Groq
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content


_PROVIDERS = {
    "gemini": _curate_with_gemini,
    "claude": _curate_with_claude,
    "openai": _curate_with_openai,
    "groq": _curate_with_groq,
}


def curate_news(raw_articles: list[dict], config: dict, market_data: dict) -> dict:
    if not raw_articles:
        logger.warning("No raw articles provided to curate_news().")
        return {"market_sentiment": "Neutral", "market_summary": "No news today.", "categories": {}}

    provider = config.get("ai_provider", "gemini")
    api_key = config.get("ai_api_key", "")
    topics = config.get("topics", "general markets")

    if provider not in _PROVIDERS:
        raise ValueError(f"Unknown AI_PROVIDER '{provider}'. Must be one of: {', '.join(_PROVIDERS)}")

    articles_block = _build_articles_block(raw_articles)
    market_data_str = json.dumps(market_data, indent=2)
    user_prompt = USER_PROMPT_TEMPLATE.format(
        topics=topics,
        market_data=market_data_str,
        articles_block=articles_block,
    )

    logger.info("Sending %d articles to %s for curation...", len(raw_articles), provider)
    raw_text = _PROVIDERS[provider](user_prompt, api_key)
    curated = _safe_parse_json(raw_text)
    logger.info("Curation complete. Sentiment: %s", curated.get("market_sentiment", "Unknown"))
    return curated
