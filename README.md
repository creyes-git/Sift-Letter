# 📈 Sift-Letter: Automated AI Finance Newsletter

Sift-Letter is a fully automated pipeline that scrapes top financial news sources, uses Google Gemini AI to curate and summarize market sentiment, and delivers a professional HTML digest directly to your inbox every morning — all for **free**, running on GitHub's servers with no local setup required.

---

## What It Does

Every day at a scheduled time, the pipeline automatically:

1. Fetches live prices for the S&P 500, Nasdaq, Bitcoin, and the 10-Year Yield
2. Scrapes financial news from the sources you configure
3. Sends all articles to Google Gemini, which filters out junk, removes duplicates, categorizes stories, and writes a 2-sentence summary for each one
4. Delivers a polished HTML email to your inbox with a market sentiment score (Bullish / Bearish / Neutral)

It remembers which articles it already sent you, so you never read the same story twice.

---

## What You Need Before Starting

You need accounts for **one AI provider of your choice**, plus Resend for email delivery, and GitHub to run the automation. All have free tiers sufficient for daily use.

---

### Step 0 — Choose Your AI Provider

The newsletter supports four AI providers. Pick one and get its API key.

| Provider | Model Used | Free Tier | Get Your Key |
|---|---|---|---|
| **Google Gemini** (default) | Gemini 1.5 Flash | ~1,500 req/day | [aistudio.google.com](https://aistudio.google.com/) → Get API Key |
| **Anthropic Claude** | Claude Haiku | Pay-as-you-go (very cheap) | [console.anthropic.com](https://console.anthropic.com/) → API Keys |
| **OpenAI** | GPT-4o Mini | Pay-as-you-go (very cheap) | [platform.openai.com](https://platform.openai.com/) → API Keys |
| **Groq** | Llama 3 70B | Free (rate-limited) | [console.groq.com](https://console.groq.com/) → API Keys |

> Gemini and Groq both have free tiers that comfortably cover one newsletter per day at no cost. Claude and OpenAI charge per token but are extremely cheap for this use case (fractions of a cent per run).

After getting your key, note the **Secret Name** you will use in GitHub — it depends on which provider you chose:

| Provider | GitHub Secret Name |
|---|---|
| Google Gemini | `GEMINI_API_KEY` |
| Anthropic Claude | `ANTHROPIC_API_KEY` |
| OpenAI | `OPENAI_API_KEY` |
| Groq | `GROQ_API_KEY` |

---

### Resend API Key
The service that sends the actual email to your inbox.

- Go to [https://resend.com/](https://resend.com/) and create a free account
- Once logged in, go to **API Keys** in the left sidebar → **"Create API Key"**
- Give it a name (e.g. `sift-letter`) and copy the key

> **Important:** The free tier of Resend only allows you to send emails to the address you signed up with unless you add and verify a custom domain. For personal use, just use your own email address as the recipient.

---

### A GitHub Account
GitHub is where the code lives and where the automation runs (for free).

- Go to [https://github.com/](https://github.com/) and create an account if you don't have one

---

## Setup Guide

### Step 1 — Upload the Project to GitHub

You need to create a GitHub repository and upload all the project files to it.

1. Log in to [github.com](https://github.com)
2. Click the **"+"** icon in the top right → **"New repository"**
3. Give it a name (e.g. `sift-letter`)
4. Set it to **Private** (recommended, since it will run automated tasks)
5. Click **"Create repository"**

Now upload the files. The easiest way is via the GitHub website:

6. On your new empty repository page, click **"uploading an existing file"**
7. Drag and drop all the project files into the window
8. Click **"Commit changes"**

Alternatively, if you have Git installed on your computer:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/sift-letter.git
git push -u origin main
```

---

### Step 2 — Add Your API Keys as Secrets

GitHub Secrets are encrypted variables that your automation can read but no one can see — not even you after saving them. This is where your sensitive API keys go.

1. Go to your repository on GitHub
2. Click **Settings** (the gear icon in the top navigation bar of the repo)
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click the **Secrets** tab
5. Click **"New repository secret"** and add the following:

**Required for everyone:**

| Secret Name | Value |
|---|---|
| `RESEND_API_KEY` | Your Resend API key |

**Required for your chosen AI provider (add only the one you chose):**

| Secret Name | Value |
|---|---|
| `GEMINI_API_KEY` | Your Google Gemini API key |
| `ANTHROPIC_API_KEY` | Your Anthropic Claude API key |
| `OPENAI_API_KEY` | Your OpenAI API key |
| `GROQ_API_KEY` | Your Groq API key |

For each one: paste the name exactly as shown, paste your key as the value, and click **"Add secret"**.

---

### Step 3 — Add Your Preferences as Variables

Variables store non-sensitive settings. These are visible, so never put API keys here.

1. Stay on the same **Secrets and variables → Actions** page
2. Click the **Variables** tab
3. Click **"New repository variable"** and add each of the following:

| Variable Name | Example Value | Description |
|---|---|---|
| `AI_PROVIDER` | `gemini` | Which AI to use: `gemini`, `claude`, `openai`, or `groq` |
| `NEWS_SOURCES` | `https://finance.yahoo.com/,https://www.cnbc.com/markets/` | Comma-separated list of financial news URLs to scrape |
| `INVESTMENT_FOCUS` | `Tech stocks, AI, Semiconductors, Macro-economics` | Tells the AI what topics matter to you. The more specific, the better. |
| `SUBSCRIBER_EMAIL` | `yourname@gmail.com` | The email address where the newsletter will be delivered |

> If you don't add `AI_PROVIDER`, it defaults to `gemini`.

> **Tip for NEWS_SOURCES:** Separate multiple URLs with commas and no spaces. Good sources include `https://finance.yahoo.com/`, `https://www.cnbc.com/markets/`, and `https://www.reuters.com/markets/`.

---

### Step 4 — Enable GitHub Actions

GitHub Actions is the automation system that runs the newsletter on a schedule. It is already configured in the file `.github/workflows/daily_newsletter.yml` that came with the project.

1. Go to your repository on GitHub
2. Click the **Actions** tab (between "Pull requests" and "Projects" in the top nav)
3. If you see a yellow banner asking to enable workflows, click **"I understand my workflows, go ahead and enable them"**

That's it. The newsletter will now run automatically every day.

---

### Step 5 — Run It Manually to Test

Before waiting until tomorrow, verify that everything works correctly by triggering it manually right now.

1. Go to the **Actions** tab in your repository
2. In the left sidebar, click **"Daily Finance Newsletter"**
3. Click the **"Run workflow"** button on the right side
4. Leave the dropdown set to `main` and click the green **"Run workflow"** button

A new run will appear in the list. Click on it to watch it in real time. It typically takes 2–4 minutes to complete. When it finishes, check your inbox.

**If it fails:** Click on the failed run, then click on the `run-newsletter` job to see the detailed logs. The most common issues are:
- A typo in a secret or variable name
- An API key that was copied incorrectly (check for extra spaces)
- `SUBSCRIBER_EMAIL` set to an address different from your Resend account email (on the free plan)

---

## How the Schedule Works

The newsletter is configured to run at **12:00 UTC** every day. To change this to your local time, you need to edit the schedule in `.github/workflows/daily_newsletter.yml`.

Find this line:
```yaml
- cron: '0 12 * * *'
```

The format is: `minute hour day month weekday`. To run at 7:00 AM Eastern Time (UTC-5), you would use `0 12 * * *`. To run at 7:00 AM Pacific Time (UTC-8), use `0 15 * * *`.

You can use [https://crontab.guru/](https://crontab.guru/) to easily generate the right cron expression for your timezone.

---

## Customizing Your Newsletter

### Changing News Sources
Edit the `NEWS_SOURCES` variable in your GitHub repository settings. The scraper works best with news aggregator pages (the homepage or markets section of a site) rather than individual articles. Any site that lists article links on a page will work.

### Changing Your Investment Focus
Edit the `INVESTMENT_FOCUS` variable. The more specific you are, the more relevant the AI curation will be. For example:
- `"S&P 500, dividend stocks, value investing"` for a long-term investor
- `"Crypto, DeFi, Bitcoin, Ethereum"` for a crypto-focused reader
- `"Biotech, FDA approvals, clinical trials"` for a healthcare investor

### Changing the Recipient Email
Edit the `SUBSCRIBER_EMAIL` variable. Note the Resend free-tier restriction mentioned above.

---

## Costs

| Service | Free Tier | Notes |
|---|---|---|
| Google Gemini API | ~1,500 requests/day free | Best free option for the AI step |
| Anthropic Claude | No free tier | ~$0.001 per newsletter run (Haiku pricing) |
| OpenAI | No free tier | ~$0.001 per newsletter run (GPT-4o Mini pricing) |
| Groq | Free (rate-limited) | Best free option if you want an open-source model |
| Resend | 3,000 emails/month free | Running daily uses ~30 emails/month |
| GitHub Actions | 2,000 minutes/month free | Each run uses ~3 minutes |

Running this project with **Gemini or Groq** costs **$0**. With Claude or OpenAI, expect less than **$0.05/month**.
