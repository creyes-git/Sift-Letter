# 📈 Sift-Letter: Automated AI Finance Newsletter

Sift-Letter is a fully automated pipeline that scrapes top financial news sources, uses an AI model of your choice to curate and summarize market sentiment, and delivers a polished HTML digest directly to your inbox every morning — all for **free**, running entirely on GitHub's servers with no local setup required.

---

## Table of Contents

1. [What It Does](#what-it-does)
2. [How It Works](#how-it-works)
3. [Project Structure](#project-structure)
4. [Prerequisites](#prerequisites)
   - [Step 0A — Choose Your AI Provider](#step-0a--choose-your-ai-provider)
   - [Step 0B — Create a Resend Account](#step-0b--create-a-resend-account)
   - [Step 0C — Create a GitHub Account](#step-0c--create-a-github-account)
5. [Setup Guide](#setup-guide)
   - [Step 1 — Fork or Upload the Project to GitHub](#step-1--fork-or-upload-the-project-to-github)
   - [Step 2 — Add Your API Keys as Secrets](#step-2--add-your-api-keys-as-secrets)
   - [Step 3 — Add Your Preferences as Variables](#step-3--add-your-preferences-as-variables)
   - [Step 4 — Enable GitHub Actions](#step-4--enable-github-actions)
   - [Step 5 — Set Your Delivery Time](#step-5--set-your-delivery-time)
   - [Step 6 — Run It Manually to Test](#step-6--run-it-manually-to-test)
6. [Customizing Your Newsletter](#customizing-your-newsletter)
7. [Troubleshooting](#troubleshooting)
8. [Costs](#costs)

---

## What It Does

Every morning at the time you choose, the pipeline automatically:

1. **Fetches live market data** — S&P 500, Nasdaq, Bitcoin, and the 10-Year Treasury Yield
2. **Scrapes financial news** from the sources you configure
3. **Curates with AI** — filters out junk, removes duplicate stories, categorizes articles, and writes a 2-sentence summary for each one
4. **Delivers a polished HTML email** to your inbox with a market sentiment score (Bullish / Bearish / Neutral)

It remembers which articles it already sent you, so you **never read the same story twice**.

---

## How It Works

```
GitHub Actions (runs on schedule)
        │
        ▼
  main.py  ──────────────────────────────────────────────────────┐
        │                                                         │
        ├─► market_data.py   Fetches live prices via yfinance     │
        │                                                         │
        ├─► scraper.py       Scrapes article links from your      │
        │                    configured news sources              │
        │                                                         │
        ├─► ai_processor.py  Sends articles + market data to      │
        │                    your chosen AI provider for          │
        │                    curation, ranking & summarization    │
        │                                                         │
        └─► delivery.py      Builds the HTML email and sends      │
                             it via Resend to your inbox  ◄───────┘
```

The pipeline is stateless — it runs, sends the email, saves a history of sent article URLs to avoid duplicates, and exits. No server, no database, no ongoing cost.

---

## Project Structure

```
sift-letter/
├── main.py              # Orchestrator — runs the full pipeline in order
├── scraper.py           # Fetches and parses article links from news sites
├── market_data.py       # Fetches live prices for major indices via yfinance
├── ai_processor.py      # Sends articles to your AI provider for curation
├── delivery.py          # Builds the HTML email and sends it via Resend
├── utils.py             # Config loader (reads environment variables)
├── pyproject.toml       # Python dependencies
└── .github/
    └── workflows/
        └── daily_newsletter.yml   # GitHub Actions workflow (the scheduler)
```

---

## Prerequisites

Before you start the setup, you need to collect **three things**: an AI API key, a Resend API key, and a GitHub account. This takes about 10 minutes total.

---

### Step 0A — Choose Your AI Provider

The newsletter supports four AI providers. **Pick one** and get its API key. Gemini and Groq are both completely free.

| Provider | Default Model | Free Tier | Get Your Key |
|---|---|---|---|
| **Google Gemini** ✅ *(recommended)* | `gemini-2.5-flash` | ~1,500 req/day free | [aistudio.google.com](https://aistudio.google.com/) → **Get API Key** |
| **Groq** ✅ *(free alternative)* | `llama3-70b-8192` | Free (rate-limited) | [console.groq.com](https://console.groq.com/) → **API Keys** |
| **Anthropic Claude** | `claude-haiku-4-5-20251001` | Pay-as-you-go | [console.anthropic.com](https://console.anthropic.com/) → **API Keys** |
| **OpenAI** | `gpt-4o-mini` | Pay-as-you-go | [platform.openai.com](https://platform.openai.com/) → **API Keys** |

> **Tip:** If you want zero cost, choose **Gemini** (Google account required) or **Groq** (free account). Claude and OpenAI cost fractions of a cent per run — less than $0.05/month.

Once you have your key, note which **Secret Name** you will use in GitHub:

| Provider | GitHub Secret Name |
|---|---|
| Google Gemini | `GEMINI_API_KEY` |
| Groq | `GROQ_API_KEY` |
| Anthropic Claude | `ANTHROPIC_API_KEY` |
| OpenAI | `OPENAI_API_KEY` |

---

### Step 0B — Create a Resend Account

Resend is the service that actually sends the email to your inbox. It has a generous free tier.

1. Go to [https://resend.com/](https://resend.com/) and click **Sign Up**
2. Verify your email address
3. In the dashboard, go to **API Keys** in the left sidebar
4. Click **"Create API Key"**, give it a name like `sift-letter`, and click **Add**
5. **Copy the key immediately** — it is only shown once

> ⚠️ **Important — Free Tier Restriction:** On Resend's free plan, you can only send emails to the **same email address you signed up with**. This is fine for personal use. If you want to send to a different address, you need to add and verify a custom domain in Resend.

---

### Step 0C — Create a GitHub Account

GitHub is where the code lives and where the automation runs for free.

- Go to [https://github.com/](https://github.com/) and create an account if you don't have one
- GitHub Actions gives you **2,000 free minutes per month**. Each newsletter run uses ~3 minutes, so daily use costs ~90 minutes/month — well within the free tier.

---

## Setup Guide

### Step 1 — Fork or Upload the Project to GitHub

You need your own copy of this repository on your GitHub account so you can configure it with your own API keys.

#### Option A — Fork (Recommended if viewing this on GitHub)

1. Click the **Fork** button at the top right of this repository page
2. Choose your account as the destination
3. Click **Create fork**

That's it — you now have your own copy at `https://github.com/YOUR_USERNAME/sift-letter`.

#### Option B — Upload manually (if you downloaded the files)

1. Log in to [github.com](https://github.com)
2. Click the **"+"** icon in the top right → **"New repository"**
3. Name it `sift-letter`
4. Set visibility to **Private** *(recommended — it will contain your automation schedule)*
5. Click **"Create repository"**
6. On the empty repository page, click **"uploading an existing file"**
7. Drag and drop **all** the project files and folders into the window
8. Click **"Commit changes"**

#### Option C — Git command line (if you have Git installed)

```bash
git clone https://github.com/ORIGINAL_OWNER/sift-letter.git
cd sift-letter
git remote set-url origin https://github.com/YOUR_USERNAME/sift-letter.git
git push -u origin main
```

---

### Step 2 — Add Your API Keys as Secrets

GitHub Secrets are **encrypted variables** — your automation can read them at runtime, but no one (including you) can view them after saving. This is where your sensitive API keys go.

**How to get there:**
1. Go to your repository on GitHub
2. Click **Settings** *(gear icon in the top navigation bar of the repo — not your profile settings)*
3. In the left sidebar, scroll down to **Secrets and variables** → click **Actions**
4. Click the **Secrets** tab
5. Click **"New repository secret"**

**Add these secrets:**

| Secret Name | Value | Required? |
|---|---|---|
| `RESEND_API_KEY` | Your Resend API key | ✅ Always |
| `GEMINI_API_KEY` | Your Google Gemini API key | ✅ If using Gemini |
| `GROQ_API_KEY` | Your Groq API key | ✅ If using Groq |
| `ANTHROPIC_API_KEY` | Your Anthropic Claude API key | ✅ If using Claude |
| `OPENAI_API_KEY` | Your OpenAI API key | ✅ If using OpenAI |

> Only add the key for the **one provider you chose** in Step 0A, plus `RESEND_API_KEY`. You do not need to add the others.

For each secret: type the name **exactly** as shown, paste your key as the value, and click **"Add secret"**.

---

### Step 3 — Add Your Preferences as Variables

Variables store non-sensitive configuration settings. Unlike Secrets, these are visible after saving — **never put API keys here**.

**How to get there:**
1. Stay on the same **Secrets and variables → Actions** page
2. Click the **Variables** tab
3. Click **"New repository variable"**

**Add these variables:**

| Variable Name | Example Value | Required? | Description |
|---|---|---|---|
| `AI_PROVIDER` | `gemini` | ✅ | Which AI to use. Options: `gemini`, `claude`, `openai`, `groq`. Defaults to `gemini` if not set. |
| `NEWS_SOURCES` | `https://finance.yahoo.com/,https://www.cnbc.com/markets/` | ✅ | Comma-separated list of news URLs to scrape. No spaces between URLs. |
| `INVESTMENT_FOCUS` | `Tech stocks, AI, S&P 500, Macro` | ✅ | Topics that matter to you. The AI uses this to filter and prioritize articles. |
| `SUBSCRIBER_EMAIL` | `yourname@gmail.com` | ✅ | Where the newsletter is delivered. Must match your Resend signup email on the free plan. |
| `AI_MODEL` | `gemini-2.0-flash` | ⬜ Optional | Override the default model for your provider. If empty or invalid, falls back to the provider default automatically. |

**Default models per provider** (used when `AI_MODEL` is not set):

| Provider | Default Model | Other Models You Can Try |
|---|---|---|
| `gemini` | `gemini-2.5-flash` | `gemini-2.0-flash`, `gemini-1.5-flash` |
| `groq` | `llama3-70b-8192` | `mixtral-8x7b-32768`, `llama3-8b-8192` |
| `claude` | `claude-haiku-4-5-20251001` | `claude-sonnet-4-5-20251001` |
| `openai` | `gpt-4o-mini` | `gpt-4o`, `gpt-4-turbo` |

> **Tips for `NEWS_SOURCES`:** Use the homepage or markets section of a site, not individual articles. Recommended starting set:
> ```
> https://finance.yahoo.com/,https://www.cnbc.com/markets/,https://www.reuters.com/markets/
> ```

> **Tips for `INVESTMENT_FOCUS`:** Be specific — the more detail you give, the more relevant the curation. Examples:
> - `S&P 500, dividend stocks, value investing, bonds` — long-term investor
> - `Crypto, Bitcoin, Ethereum, DeFi, altcoins` — crypto-focused
> - `Biotech, FDA approvals, clinical trials, healthcare` — healthcare investor
> - `Tech stocks, AI, semiconductors, FAANG, growth stocks` — tech-focused

---

### Step 4 — Enable GitHub Actions

GitHub Actions is the automation engine that runs the newsletter on a schedule. The workflow file is already included in the project at `.github/workflows/daily_newsletter.yml` — you just need to enable it.

1. Go to your repository on GitHub
2. Click the **Actions** tab *(in the top navigation bar, between "Pull requests" and "Projects")*
3. If you see a yellow banner that says **"Workflows aren't being run on this forked repository"**, click **"I understand my workflows, go ahead and enable them"**

That's it. The workflow is now active and will run on the configured schedule.

---

### Step 5 — Set Your Delivery Time

The newsletter is pre-configured to run at **11:00 UTC** (7:00 AM Eastern Time / Miami). If you are in a different timezone, you need to update the schedule.

**How to change it:**

1. In your repository, navigate to `.github/workflows/daily_newsletter.yml`
2. Click the **pencil icon** (Edit) in the top right of the file view
3. Find this line near the top:
   ```yaml
   - cron: '0 11 * * *'
   ```
4. Change the hour (`11`) to match your timezone offset from UTC
5. Click **"Commit changes"**

**Common timezone references for 7:00 AM delivery:**

| Timezone | UTC Offset (Summer) | UTC Offset (Winter) | Cron Expression |
|---|---|---|---|
| Miami / New York (ET) | UTC-4 | UTC-5 | `0 11 * * *` / `0 12 * * *` |
| Chicago (CT) | UTC-5 | UTC-6 | `0 12 * * *` / `0 13 * * *` |
| Denver (MT) | UTC-6 | UTC-7 | `0 13 * * *` / `0 14 * * *` |
| Los Angeles (PT) | UTC-7 | UTC-8 | `0 14 * * *` / `0 15 * * *` |
| London (BST/GMT) | UTC+1 | UTC+0 | `0 6 * * *` / `0 7 * * *` |
| Paris / Berlin (CET) | UTC+2 | UTC+1 | `0 5 * * *` / `0 6 * * *` |

> The cron format is: `minute hour day-of-month month day-of-week`. Use [crontab.guru](https://crontab.guru/) to generate any expression you need.

> ⚠️ **Daylight Saving Time:** GitHub Actions uses UTC, which never changes. When your local clock shifts in spring or fall, you need to manually update the cron hour by ±1 to keep the 7 AM delivery time.

---

### Step 6 — Run It Manually to Test

Before waiting until tomorrow morning, trigger a manual run right now to verify everything is configured correctly.

1. Go to the **Actions** tab in your repository
2. In the left sidebar, click **"Daily Finance Newsletter"**
3. Click the **"Run workflow"** dropdown button on the right side
4. Leave the branch set to `main` and click the green **"Run workflow"** button

A new run will appear in the list within a few seconds. Click on it to watch the live logs. It typically takes **2–4 minutes** to complete. When it finishes with a green checkmark ✅, check your inbox.

---

## Customizing Your Newsletter

### Changing News Sources

Edit the `NEWS_SOURCES` variable in **Settings → Secrets and variables → Actions → Variables**. The scraper works best with news aggregator pages (a site's homepage or markets section) rather than individual article URLs.

Any site that lists article links on a page will work. Some good options:

```
https://finance.yahoo.com/
https://www.cnbc.com/markets/
https://www.reuters.com/markets/
https://www.marketwatch.com/
https://www.bloomberg.com/markets
https://www.ft.com/markets
```

### Changing Your Investment Focus

Edit the `INVESTMENT_FOCUS` variable. The AI uses this to decide which articles to keep and which to discard. The more specific you are, the more relevant the output.

### Changing the AI Provider or Model

- To switch providers: update the `AI_PROVIDER` variable and add the corresponding API key as a Secret
- To try a different model: set the `AI_MODEL` variable to any valid model name for your provider. If the name is wrong, the pipeline will log a warning and automatically fall back to the provider's default — the newsletter will still be delivered

### Changing the Delivery Time

Edit the cron expression in `.github/workflows/daily_newsletter.yml` as described in Step 5.

### Changing the Recipient Email

Edit the `SUBSCRIBER_EMAIL` variable. Remember the Resend free-tier restriction: the recipient must be the same email you used to sign up for Resend, unless you have verified a custom domain.

---

## Troubleshooting

If a run fails, go to **Actions** → click the failed run → click the `run-newsletter` job to see the full logs. Here are the most common issues:

| Symptom | Likely Cause | Fix |
|---|---|---|
| `Missing required environment variables` | A Secret or Variable name has a typo, or wasn't added | Double-check all names in Settings → Secrets and variables. Names are case-sensitive. |
| `Invalid API key` | The key was copied with extra spaces, or is incorrect | Delete the secret and re-add it. Make sure there are no leading/trailing spaces. |
| Email not received | `SUBSCRIBER_EMAIL` doesn't match your Resend signup email | On the free plan, recipient must match your Resend account email. |
| `No articles scraped` | The news source blocked the scraper, or the URL is wrong | Try a different URL or add more sources to `NEWS_SOURCES`. |
| `LLM returned invalid JSON` | The AI model returned a malformed response | This is rare. Re-run the workflow — it usually succeeds on the next attempt. |
| `Groq model invalid` | The model name in `AI_MODEL` doesn't exist for Groq | The pipeline will auto-retry with the default. Check the logs for the warning message. |
| Actions tab shows no workflows | Workflows weren't enabled after forking | Go to the Actions tab and click "enable workflows". |
| Run triggers but nothing happens | The workflow file has a YAML syntax error | Validate `.github/workflows/daily_newsletter.yml` at [yamllint.com](https://www.yamllint.com/). |

---

## Costs

Everything needed to run this project has a free tier. Running with Gemini or Groq costs **$0**.

| Service | Free Tier | Monthly Usage | Cost |
|---|---|---|---|
| **GitHub Actions** | 2,000 min/month | ~90 min/month (daily runs) | **Free** |
| **Google Gemini API** | ~1,500 req/day | 1 req/day | **Free** |
| **Groq API** | Free (rate-limited) | 1 req/day | **Free** |
| **Resend** | 3,000 emails/month | ~30 emails/month | **Free** |
| **Anthropic Claude** | None | 1 req/day | ~$0.03/month |
| **OpenAI** | None | 1 req/day | ~$0.03/month |

> All free tiers are sufficient for one newsletter per day with significant headroom to spare.
