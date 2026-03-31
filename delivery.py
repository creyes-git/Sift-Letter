"""
delivery.py – Formats curated financial news into a styled HTML email and sends it via Resend.
"""

import html
import logging
from datetime import datetime

import resend

logger = logging.getLogger(__name__)

def _sentiment_badge(sentiment: str) -> str:
    color = "#16a34a" if sentiment.lower() == "bullish" else "#dc2626" if sentiment.lower() == "bearish" else "#d97706"
    icon = "🐂" if sentiment.lower() == "bullish" else "🐻" if sentiment.lower() == "bearish" else "⚖️"
    return f'<span style="background:{color};color:#fff;padding:4px 12px;border-radius:12px;font-size:14px;font-weight:bold;">{icon} {sentiment.upper()}</span>'

def _impact_badge(score: int) -> str:
    color = "#dc2626" if score >= 8 else "#d97706" if score >= 5 else "#16a34a"
    return f'<span style="background:{color};color:#fff;padding:2px 8px;border-radius:8px;font-size:11px;font-weight:bold;">IMPACT {score}/10</span>'

def _render_market_snapshot(market_data: dict) -> str:
    cards = []
    for name, data in market_data.items():
        price = data.get("price", 0.0)
        pct = data.get("change_pct", 0.0)
        color = "#16a34a" if pct >= 0 else "#dc2626"
        sign = "+" if pct >= 0 else ""
        cards.append(f"""
        <div style="flex:1;min-width:120px;background:#f8fafc;padding:12px;border-radius:8px;margin:4px;text-align:center;border:1px solid #e2e8f0;">
            <div style="font-size:12px;color:#64748b;font-weight:bold;">{name}</div>
            <div style="font-size:16px;color:#1e293b;font-weight:bold;margin:4px 0;">${price:,.2f}</div>
            <div style="font-size:13px;color:{color};font-weight:bold;">{sign}{pct:.2f}%</div>
        </div>
        """)
    return f'<div style="display:flex;flex-wrap:wrap;margin:0 -4px;">{"".join(cards)}</div>'

def _render_article(article: dict) -> str:
    title = html.escape(article.get("title", "Untitled"))
    summary = html.escape(article.get("summary", ""))
    link = html.escape(article.get("link", "#"))
    score = int(article.get("impact_score", 0))

    return f"""
    <div style="margin-bottom:20px;padding-bottom:20px;border-bottom:1px solid #e2e8f0;">
      <div style="margin-bottom:8px;">{_impact_badge(score)}</div>
      <h3 style="margin:0 0 8px 0;font-size:16px;line-height:1.4;">
        <a href="{link}" style="color:#0f172a;text-decoration:none;font-weight:bold;">{title}</a>
      </h3>
      <p style="margin:0;color:#475569;font-size:14px;line-height:1.6;">{summary}</p>
    </div>"""

def _build_html_email(curated_data: dict, market_data: dict, topics: str, ai_provider: str = "gemini") -> str:
    today = datetime.now().strftime("%B %d, %Y")
    sentiment = curated_data.get("market_sentiment", "Neutral")
    summary = curated_data.get("market_summary", "")
    categories = curated_data.get("categories", {})

    categories_html = ""
    for cat_name, articles in categories.items():
        if not articles:
            continue
        sorted_articles = sorted(articles, key=lambda a: a.get("impact_score", 0), reverse=True)
        articles_html = "".join(_render_article(art) for art in sorted_articles)
        categories_html += f"""
        <h2 style="color:#4f46e5;font-size:18px;margin:30px 0 16px 0;border-bottom:2px solid #e0e7ff;padding-bottom:8px;">
            {cat_name}
        </h2>
        {articles_html}
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI Finance Digest – {today}</title>
</head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f1f5f9;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="640" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 4px 6px -1px rgba(0,0,0,0.1);">
          
          <!-- Header -->
          <tr>
            <td style="background:#0f172a;padding:36px 40px;text-align:center;">
              <h1 style="margin:0;color:#ffffff;font-size:26px;letter-spacing:-0.5px;">📈 The AI Finance Digest</h1>
              <p style="margin:8px 0 0 0;color:#94a3b8;font-size:14px;">{today}</p>
            </td>
          </tr>

          <!-- Market Snapshot -->
          <tr>
            <td style="padding:24px 40px;background:#ffffff;border-bottom:1px solid #e2e8f0;">
              <div style="margin-bottom:20px;display:flex;justify-content:space-between;align-items:center;">
                <span style="font-size:14px;color:#64748b;font-weight:bold;text-transform:uppercase;">Market Snapshot</span>
                {_sentiment_badge(sentiment)}
              </div>
              {_render_market_snapshot(market_data)}
              <p style="margin:20px 0 0 0;font-size:15px;line-height:1.6;color:#334155;background:#f8fafc;padding:16px;border-left:4px solid #3b82f6;border-radius:4px;">
                <strong>AI Market Summary:</strong> {summary}
              </p>
            </td>
          </tr>

          <!-- Articles by Category -->
          <tr>
            <td style="padding:10px 40px 32px 40px;">
              {categories_html}
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#f8fafc;padding:24px 40px;text-align:center;border-top:1px solid #e2e8f0;">
              <p style="margin:0;font-size:12px;color:#94a3b8;">
                Curated based on: <em>{topics}</em><br><br>
                Powered by {ai_provider.capitalize()} &amp; yfinance
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

def send_newsletter(curated_data: dict, market_data: dict, config: dict) -> None:
    api_key = config.get("resend_api_key", "")
    to_email = config.get("subscriber_email", "")
    topics = config.get("topics", "general markets")

    if not api_key:
        raise ValueError("resend_api_key is missing from config.")
    if not to_email:
        raise ValueError("subscriber_email is missing from config.")

    resend.api_key = api_key
    today = datetime.now().strftime("%B %d, %Y")
    ai_provider = config.get("ai_provider", "gemini")
    html_body = _build_html_email(curated_data, market_data, topics, ai_provider)

    logger.info("Sending finance newsletter to %s via Resend...", to_email)

    response = resend.Emails.send(
        {
            "from": "AI Finance <newsletter@resend.dev>",
            "to": [to_email],
            "subject": f"📈 AI Market Digest – {today}",
            "html": html_body,
        }
    )

    logger.info("Email sent successfully. Resend response: %s", response)
