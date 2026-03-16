#!/usr/bin/env python3
"""
fetch_rss.py — Fetches RSS feeds, cleans HTML, extracts tags, writes articles.json.
Zero external API usage. Runs daily via GitHub Actions.
"""

import json
import hashlib
import datetime
import sys
import time
import re
from pathlib import Path

try:
    import feedparser
    import requests
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "feedparser", "requests"])
    import feedparser
    import requests

RSS_FEEDS = [
    {"name": "OpenAI Blog",          "url": "https://openai.com/blog/rss.xml",                               "category": "AI Models"},
    {"name": "DeepMind Blog",        "url": "https://deepmind.google/blog/rss.xml",                          "category": "Research"},
    {"name": "Anthropic Blog",       "url": "https://www.anthropic.com/rss.xml",                             "category": "AI Models"},
    {"name": "Meta AI Blog",         "url": "https://ai.meta.com/blog/rss/",                                 "category": "AI Models"},
    {"name": "TechCrunch AI",        "url": "https://techcrunch.com/category/artificial-intelligence/feed/", "category": "AI Startups"},
    {"name": "VentureBeat AI",       "url": "https://venturebeat.com/category/ai/feed/",                     "category": "AI Tools"},
    {"name": "MIT Tech Review",      "url": "https://www.technologyreview.com/feed/",                        "category": "Research"},
    {"name": "The Gradient",         "url": "https://thegradient.pub/rss/",                                  "category": "Research"},
    {"name": "Towards Data Science", "url": "https://towardsdatascience.com/feed",                           "category": "Research"},
    {"name": "Hugging Face Blog",    "url": "https://huggingface.co/blog/feed.xml",                          "category": "AI Tools"},
    {"name": "Google AI Blog",       "url": "https://blog.google/technology/ai/rss/",                        "category": "AI Models"},
    {"name": "NVIDIA AI Blog",       "url": "https://blogs.nvidia.com/blog/category/deep-learning/feed/",    "category": "AI Tools"},
]

OUTPUT_FILE  = Path("data/articles.json")
MAX_PER_FEED = 5
MAX_TOTAL    = 300

KEYWORD_TAGS = {
    r"gpt":                "GPT",
    r"chatgpt":            "ChatGPT",
    r"claude":             "Claude",
    r"gemini":             "Gemini",
    r"\bllm\b":            "LLM",
    r"large language":     "LLM",
    r"transformer":        "transformers",
    r"diffusion":          "diffusion",
    r"open.?source":       "open-source",
    r"benchmark":          "benchmark",
    r"fine.?tun":          "fine-tuning",
    r"\brag\b":            "RAG",
    r"retrieval":          "RAG",
    r"\bagent":            "agents",
    r"multimodal":         "multimodal",
    r"computer.?vision":   "computer-vision",
    r"robot":              "robotics",
    r"regulation":         "regulation",
    r"safety":             "safety",
    r"alignment":          "alignment",
    r"startup":            "startups",
    r"funding":            "funding",
    r"open.?ai":           "OpenAI",
    r"anthropic":          "Anthropic",
    r"mistral":            "Mistral",
    r"hugging.?face":      "HuggingFace",
    r"\bnvidia\b":         "NVIDIA",
    r"\bgpu\b":            "hardware",
    r"inference":          "inference",
}

CATEGORY_KEYWORDS = {
    "AI Models":   ["gpt", "claude", "gemini", "llm", "language model", "foundation model"],
    "Research":    ["paper", "arxiv", "research", "study", "benchmark", "dataset"],
    "Robotics":    ["robot", "robotics", "embodied", "drone", "autonomous vehicle"],
    "AI Policy":   ["regulation", "policy", "law", "eu ai act", "safety", "alignment", "ethics"],
    "AI Startups": ["startup", "funding", "raise", "series", "valuation", "launch"],
    "AI Tools":    ["tool", "app", "product", "release", "update", "feature", "api", "platform"],
}


def strip_html(text):
    text = re.sub(r"<[^>]+>", " ", text)
    for ent, ch in [("&amp;","&"),("&lt;","<"),("&gt;",">"),("&quot;",'"'),("&#39;","'"),("&nbsp;"," ")]:
        text = text.replace(ent, ch)
    return re.sub(r"\s+", " ", text).strip()


def extract_tags(text):
    text_lower = text.lower()
    found = []
    for pattern, tag in KEYWORD_TAGS.items():
        if re.search(pattern, text_lower) and tag not in found:
            found.append(tag)
    return found[:6]


def infer_category(title, summary, default):
    combined = (title + " " + summary).lower()
    scores = {cat: sum(1 for kw in kws if kw in combined) for cat, kws in CATEGORY_KEYWORDS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else default


def clean_summary(raw, max_len=300):
    cleaned = strip_html(raw)
    if len(cleaned) > max_len:
        trunc = cleaned[:max_len]
        last = trunc.rfind(". ")
        return (trunc[:last+1] if last > 100 else trunc.rstrip() + "…")
    return cleaned


def make_id(url):
    return "rss-" + hashlib.md5(url.encode()).hexdigest()[:8]


def fetch_feed(source):
    print(f"  Fetching: {source['name']}")
    try:
        feed = feedparser.parse(source["url"])
        articles = []
        for entry in feed.entries[:MAX_PER_FEED]:
            pub = entry.get("published", entry.get("updated", datetime.datetime.utcnow().isoformat()))
            raw = entry.get("summary", entry.get("description", ""))
            title   = strip_html(entry.get("title", "Untitled"))
            summary = clean_summary(raw)
            articles.append({
                "id":             make_id(entry.get("link", "")),
                "title":          title,
                "summary":        summary,
                "bullets":        [],
                "why_it_matters": "",
                "source":         source["name"],
                "url":            entry.get("link", ""),
                "tags":           extract_tags(title + " " + summary),
                "category":       infer_category(title, summary, source["category"]),
                "published_date": pub,
                "image":          None,
            })
        print(f"    + {len(articles)} articles")
        return articles
    except Exception as e:
        print(f"    ERROR: {e}")
        return []


def main():
    print("=== AI Pulse RSS Fetcher ===")
    existing_ids = set()
    existing = []
    if OUTPUT_FILE.exists():
        try:
            with open(OUTPUT_FILE) as f:
                existing = json.load(f)
                existing_ids = {a["id"] for a in existing}
        except Exception:
            pass

    new_count = 0
    for source in RSS_FEEDS:
        for article in fetch_feed(source):
            if article["id"] not in existing_ids:
                existing.append(article)
                existing_ids.add(article["id"])
                new_count += 1
        time.sleep(0.3)

    existing.sort(key=lambda x: x.get("published_date", ""), reverse=True)
    existing = existing[:MAX_TOTAL]

    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(existing, f, indent=2)

    print(f"\nDone. {new_count} new articles. Total: {len(existing)}")


if __name__ == "__main__":
    main()
