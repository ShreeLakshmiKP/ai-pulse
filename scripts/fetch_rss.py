#!/usr/bin/env python3
import json, hashlib, datetime, sys, time, re
from pathlib import Path

try:
    import feedparser
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "feedparser"])
    import feedparser

RSS_FEEDS = [
    {"name": "OpenAI Blog",          "url": "https://openai.com/blog/rss.xml",                               "category": "AI Models"},
    {"name": "DeepMind Blog",        "url": "https://deepmind.google/blog/rss.xml",                          "category": "Research"},
    {"name": "Anthropic Blog",       "url": "https://www.anthropic.com/rss.xml",                             "category": "AI Models"},
    {"name": "Meta AI Blog",         "url": "https://ai.meta.com/blog/rss/",                                 "category": "AI Models"},
    {"name": "TechCrunch AI",        "url": "https://techcrunch.com/category/artificial-intelligence/feed/", "category": "AI Startups"},
    {"name": "VentureBeat AI",       "url": "https://venturebeat.com/category/ai/feed/",                     "category": "AI Tools"},
    {"name": "MIT Tech Review",      "url": "https://www.technologyreview.com/feed/",                        "category": "Research"},
    {"name": "Hugging Face Blog",    "url": "https://huggingface.co/blog/feed.xml",                          "category": "AI Tools"},
    {"name": "Google AI Blog",       "url": "https://blog.google/technology/ai/rss/",                        "category": "AI Models"},
    {"name": "The Gradient",         "url": "https://thegradient.pub/rss/",                                  "category": "Research"},
]

OUTPUT_FILE = Path("data/articles.json")
MAX_PER_FEED = 5
MAX_TOTAL = 300

KEYWORD_TAGS = {
    r"gpt": "GPT", r"chatgpt": "ChatGPT", r"claude": "Claude",
    r"gemini": "Gemini", r"\bllm\b": "LLM", r"transformer": "transformers",
    r"open.?source": "open-source", r"benchmark": "benchmark",
    r"\bagent": "agents", r"multimodal": "multimodal",
    r"robot": "robotics", r"regulation": "regulation",
    r"safety": "safety", r"alignment": "alignment",
    r"startup": "startups", r"funding": "funding",
    r"open.?ai": "OpenAI", r"anthropic": "Anthropic",
    r"mistral": "Mistral", r"\bnvidia\b": "NVIDIA",
    r"\bgpu\b": "hardware", r"inference": "inference",
}

CATEGORY_KEYWORDS = {
    "AI Models":   ["gpt", "claude", "gemini", "llm", "language model", "foundation model"],
    "Research":    ["paper", "arxiv", "research", "study", "benchmark", "dataset"],
    "Robotics":    ["robot", "robotics", "embodied", "drone"],
    "AI Policy":   ["regulation", "policy", "law", "safety", "alignment", "ethics"],
    "AI Startups": ["startup", "funding", "raise", "series", "valuation"],
    "AI Tools":    ["tool", "app", "product", "release", "update", "api", "platform"],
}

def strip_html(text):
    text = re.sub(r"<[^>]+>", " ", text)
    for ent, ch in [("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'), ("&nbsp;", " ")]:
