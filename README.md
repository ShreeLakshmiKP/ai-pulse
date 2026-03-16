# ⚡ AI Pulse

> Automated daily AI news and tools discovery — **100% free**, no API keys needed.

[![Daily Pipeline](https://github.com/YOUR_USERNAME/ai-pulse/actions/workflows/daily-pipeline.yml/badge.svg)](https://github.com/YOUR_USERNAME/ai-pulse/actions)
[![Deploy](https://github.com/YOUR_USERNAME/ai-pulse/actions/workflows/deploy-pages.yml/badge.svg)](https://github.com/YOUR_USERNAME/ai-pulse/actions)

**Live demo**: `https://YOUR_USERNAME.github.io/ai-pulse`

---

## What It Does

AI Pulse automatically:

1. **Fetches** RSS feeds from 12 AI blogs (OpenAI, DeepMind, Anthropic, Meta AI, TechCrunch, VentureBeat, HuggingFace, NVIDIA, and more)
2. **Extracts tags** using keyword matching (no AI needed)
3. **Categorizes** articles into: AI Models, AI Tools, Research, Robotics, AI Startups, AI Policy
4. **Pulls** trending discussions from Hacker News API (free)
5. **Monitors** trending AI repos on GitHub (free, token auto-provided by Actions)
6. **Generates** a daily digest using pure Python — top stories by category spread
7. **Deploys** the site to GitHub Pages automatically

**No ANTHROPIC_API_KEY. No paid APIs. No secrets to configure at all.**

---

## Project Structure

```
ai-pulse/
├── index.html                    # Full website — Home, News, Tools, Trending, Submit
├── data/
│   ├── articles.json             # AI news (auto-updated daily)
│   ├── tools.json                # AI tools directory (edit manually or extend)
│   ├── digest.json               # Daily AI digest (auto-generated)
│   ├── categories.json           # Category definitions
│   ├── hn_stories.json           # HN top AI stories (auto-updated)
│   └── github_trending.json      # Trending GitHub AI repos (auto-updated)
├── scripts/
│   ├── fetch_rss.py              # Fetches 12 RSS feeds → articles.json
│   ├── fetch_apis.py             # Fetches HN + GitHub data
│   └── generate_digest.py        # Builds digest from articles (pure Python)
├── .github/workflows/
│   ├── daily-pipeline.yml        # Runs daily at 6 AM UTC
│   └── deploy-pages.yml          # Deploys on every push
├── requirements.txt              # feedparser + requests only
└── README.md
```

---

## Quick Start (3 Steps)

### 1. Fork / Clone

```bash
git clone https://github.com/YOUR_USERNAME/ai-pulse.git
cd ai-pulse
```

### 2. Enable GitHub Pages

1. Go to **Settings → Pages**
2. Source: **GitHub Actions**
3. Save

### 3. Trigger First Run

1. Go to **Actions → Daily AI Data Pipeline**
2. Click **Run workflow**

That's it. No secrets, no API keys, nothing to configure.

Your site will be live at: `https://YOUR_USERNAME.github.io/ai-pulse`

---

## Automation Schedule

Runs **daily at 6 AM UTC**. Change in `.github/workflows/daily-pipeline.yml`:

```yaml
schedule:
  - cron: '0 6 * * *'
```

---

## Adding More RSS Sources

Edit `scripts/fetch_rss.py`:

```python
RSS_FEEDS = [
    # Add your source here:
    {"name": "My Blog", "url": "https://myblog.com/feed.xml", "category": "Research"},
]
```

## Adding AI Tools

Edit `data/tools.json` directly. Each entry:

```json
{
  "id": "tool-007",
  "name": "My Tool",
  "description": "What it does.",
  "category": "Developer Tools",
  "website": "https://mytool.com",
  "tags": ["coding", "ai"],
  "features": ["Feature 1", "Feature 2"],
  "pricing": "Freemium",
  "upvotes": 100,
  "trending": false
}
```

---

## Cost

| Item | Cost |
|------|------|
| GitHub Pages | **Free** |
| GitHub Actions | **Free** (2,000 min/month included) |
| Anthropic / OpenAI API | **Not used** |
| Any other paid API | **Not used** |
| **Total** | **$0/month** |

---

## License

MIT — fork freely.
