#!/usr/bin/env python3
import json, datetime, sys, os, time
from pathlib import Path

try:
    import requests
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

HN_SEARCH  = "https://hn.algolia.com/api/v1/search"
GH_SEARCH  = "https://api.github.com/search/repositories"
AI_TOPICS  = ["ai", "machine-learning", "llm", "generative-ai"]
AI_QUERIES = ["AI", "LLM", "GPT", "Claude", "Gemini", "machine learning"]

def fetch_hn():
    print("Fetching Hacker News AI stories...")
    yesterday = int((datetime.datetime.utcnow() - datetime.timedelta(days=1)).timestamp())
    stories, seen = [], set()
    for q in AI_QUERIES:
        try:
            r = requests.get(HN_SEARCH, params={
                "query": q, "tags": "story",
                "numericFilters": f"created_at_i>{yesterday},points>10",
                "hitsPerPage": 10,
            }, timeout=10)
            for hit in r.json().get("hits", []):
                if hit["objectID"] not in seen:
                    seen.add(hit["objectID"])
                    stories.append({
                        "id":             f"hn-{hit['objectID']}",
                        "title":          hit.get("title", ""),
                        "url":            hit.get("url") or f"https://news.ycombinator.com/item?id={hit['objectID']}",
                        "points":         hit.get("points", 0),
                        "comments":       hit.get("num_comments", 0),
                        "source":         "Hacker News",
                        "published_date": hit.get("created_at", ""),
                    })
        except Exception as e:
            print(f"  HN '{q}': {e}")
        time.sleep(0.2)
    stories.sort(key=lambda x: x["points"], reverse=True)
    print(f"  + {len(stories)} stories")
    return stories[:20]

def fetch_github():
    print("Fetching GitHub trending AI repos...")
    headers = {}
    token = os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    repos, seen = [], set()
    week_ago = (datetime.datetime.utcnow() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    for topic in AI_TOPICS:
        try:
            r = requests.get(GH_SEARCH, headers=headers, params={
                "q": f"topic:{topic} created:>{week_ago}",
                "sort": "stars", "order": "desc", "per_page": 5,
            }, timeout=10)
            for repo in r.json().get("items", []):
                if repo["id"] not in seen:
                    seen.add(repo["id"])
                    repos.append({
                        "id":          f"gh-{repo['id']}",
                        "name":        repo["full_name"],
                        "description": repo.get("description", ""),
                        "url":         repo["html_url"],
                        "stars":       repo["stargazers_count"],
                        "language":    repo.get("language", ""),
                        "topics":      repo.get("topics", []),
                        "created_at":  repo.get("created_at", ""),
                    })
        except Exception as e:
            print(f"  GitHub '{topic}': {e}")
        time.sleep(0.3)
    repos.sort(key=lambda x: x["stars"], reverse=True)
    print(f"  + {len(repos)} repos")
    return repos[:15]

def main():
    print("=== AI Pulse API Fetcher ===")
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    with open(data_dir / "hn_stories.json", "w") as f:
        json.dump(fetch_hn(), f, indent=2)
    with open(data_dir / "github_trendin
