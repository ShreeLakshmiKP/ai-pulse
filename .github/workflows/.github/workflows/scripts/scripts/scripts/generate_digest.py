#!/usr/bin/env python3
"""
generate_digest.py — Builds the daily digest from articles.json using pure Python.
Zero API cost. Picks top articles by recency and category spread.
"""

import json, datetime, re
from pathlib import Path
from collections import Counter

ARTICLES_FILE = Path("data/articles.json")
TOOLS_FILE    = Path("data/tools.json")
OUTPUT_FILE   = Path("data/digest.json")

TYPE_MAP = {
    "AI Models":   "model",
    "Research":    "research",
    "AI Policy":   "policy",
    "AI Tools":    "tool",
    "AI Startups": "tool",
    "Robotics":    "research",
}

def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")

def main():
    print("=== AI Pulse Digest Generator ===")

    articles = json.loads(ARTICLES_FILE.read_text()) if ARTICLES_FILE.exists() else []
    tools    = json.loads(TOOLS_FILE.read_text())    if TOOLS_FILE.exists()    else []

    # ── Pick top 5 articles spread across categories ──────────────────────────
    seen_cats = set()
    top_articles = []
    for a in articles[:40]:
        if a["category"] not in seen_cats or len(top_articles) < 3:
            top_articles.append(a)
            seen_cats.add(a["category"])
        if len(top_articles) == 5:
            break

    # ── Build highlights from top articles ────────────────────────────────────
    highlights = []
    for a in top_articles:
        hi_type = TYPE_MAP.get(a["category"], "tool")
        # Shorten title to ~80 chars
        text = a["title"] if len(a["title"]) <= 80 else a["title"][:77] + "…"
        highlights.append({"type": hi_type, "text": text})

    # ── Headline: join top 3 source names + date ──────────────────────────────
    sources = [a["source"] for a in top_articles[:3]]
    headline = " · ".join(sources) if sources else "Daily AI Digest"

    # ── Top story: first article summary (first 2 sentences) ──────────────────
    top_story = ""
    if top_articles:
        sentences = re.split(r'(?<=[.!?])\s+', top_articles[0]["summary"])
        top_story = " ".join(sentences[:2])

    # ── Category distribution stat ────────────────────────────────────────────
    cat_counts = Counter(a["category"] for a in articles[:50])
    top_cat, top_n = cat_counts.most_common(1)[0] if cat_counts else ("AI", 0)
    stat = f"Today's feed: {len(articles[:50])} articles — {top_n} in {top_cat}."

    # ── Trending tools ─────────────────────────────────────────────────────────
    trending_tool_ids = [t["id"] for t in tools if t.get("trending")][:4]
    top_article_ids   = [a["id"] for a in top_articles[:3]]

    digest = {
        "date":           datetime.date.today().isoformat(),
        "headline":       headline,
        "top_story":      top_story,
        "highlights":     highlights,
        "stat_of_the_day": stat,
        "trending_tools": trending_tool_ids,
        "top_articles":   top_article_ids,
    }

    OUTPUT_FILE.write_text(json.dumps(digest, indent=2))
    print(f"Digest saved. Headline: {headline}")

if __name__ == "__main__":
    main()
