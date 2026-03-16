#!/usr/bin/env python3
import json
import hashlib
import datetime
import sys
import time
import re
from pathlib import Path

try:
    import feedparser
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "feedparser"])
    import feedparser

RSS_FEEDS = [
    {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss.xml", "category": "AI Models"},
    {"name": "DeepMind Blog", "url": "https://deepmind.google/blog/rss.xml", "category": "Research"},
    {"name": "Anthropic Blog", "url": "https://www.anthropic.com/rss.xml", "category": "AI Models"},
    {"name": "Meta AI Blog", "url": "https://ai.meta.com/blog/rss/", "category": "AI Models"},
    {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/", "category": "AI Startups"},
    {"name": "VentureBeat AI", "url": "https://venturebeat.com/category/ai/feed/", "category": "AI Tools"},
    {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/", "category": "Research"},
    {"name": "Hugging Face Blog", "url": "https://huggingface.co/blog/feed.xml", "category": "AI Tools"},
    {"name": "Google AI Blog", "url": "https://blog.google/technology/ai/rss/", "category": "AI Models"},
    {"name": "The Gradient", "url": "https://thegradient.pub/rss/", "category": "Research"},
]

OUTPUT_FILE = Path("data/articles.json")
MAX_PER_FEED = 5
MAX_TOTAL = 300

KEYWORD_TAGS = {
    "gpt": "GPT",
    "chatgpt": "ChatGPT",
    "claude": "Claude",
    "gemini": "Gemini",
    "llm": "LLM",
    "transformer": "transformers",
    "open-source": "open-source",
    "benchmark": "benchmark",
    "agent": "agents",
    "multimodal": "multimodal",
    "robot": "robotics",
    "regulation": "regulation",
    "safety": "safety",
    "alignment": "alignment",
    "startup": "startups",
    "funding": "funding",
    "openai": "OpenAI",
    "anthropic": "Anthropic",
    "mistral": "Mistral",
    "nvidia": "NVIDIA",
    "inference": "inference",
}

CATEGORY_KEYWORDS = {
    "AI Models": ["gpt", "claude", "gemini", "llm", "language model", "foundation model"],
    "Research": ["paper", "arxiv", "research", "study", "benchmark", "dataset"],
    "Robotics": ["robot", "robotics", "embodied", "drone"],
    "AI Policy": ["regulation", "policy", "law", "safety", "alignment", "ethics"],
    "AI Startups": ["startup", "funding", "raise", "series", "valuation"],
    "AI Tools": ["tool", "app", "product", "release", "update", "api", "platform"],
}


def strip_html(text):
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("&amp;", "&")
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    text = text.replace("&quot;", '"')
    text = text.replace("&nbsp;", " ")
    return re.sub(r"\s+", " ", text).strip()


def extract_tags(text):
    text_lower = text.lower()
    found = []
    for keyword, tag in KEYWORD_TAGS.items():
        if keyword in text_lower and tag not in found:
            found.append(tag)
    return found[:6]


def infer_category(title, summary, default):
    combined = (title + " " + summary).lower()
    scores = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        scores[cat] = sum(1 for kw in keywords if kw in combined)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else default


def clean_summary(raw, max_len=300):
    cleaned = strip_html(raw)
    if len(cleaned) > max_len:
        trunc = cleaned[:max_len]
        last = trunc.rfind(". ")
        if last > 100:
            return trunc[:last + 1]
        return trunc.rstrip() + "..."
    return cleaned


def make_id(url):
    return "rss-" + hashlib.md5(url.encode()).hexdigest()[:8]


def fetch_feed(source):
    print("  Fetching: " + source["name"])
    try:
        feed = feedparser.parse(source["url"])
        articles = []
        for entry in feed.entries[:MAX_PER_FEED]:
            pub = entry.get("published", entry.get("updated", datetime.datetime.utcnow().isoformat()))
            raw = entry.get("summary", entry.get("description", ""))
            title = strip_html(entry.get("title", "Untitled"))
            summary = clean_summary(raw)
            articles.append({
                "id": make_id(entry.get("link", "")),
                "title": title,
                "summary": summary,
                "bullets": [],
                "why_it_matters": "",
                "source": source["name"],
                "url": entry.get("link", ""),
                "tags": extract_tags(title + " " + summary),
                "category": infer_category(title, summary, source["category"]),
                "published_date": pub,
                "image": None,
            })
        print("    + " + str(len(articles)) + " articles")
        return articles
    except Exception as e:
        print("    ERROR: " + str(e))
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

    print("Done. " + str(new_count) + " new articles. Total: " + str(len(existing)))


if __name__ == "__main__":
    main()
