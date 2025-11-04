#!/usr/bin/env python3
"""
Fetches latest items from a list of RSS/Atom feeds (AI-related)
and injects them as markdown into README.md between markers:
<!-- NEWS_START --> and <!-- NEWS_END -->
"""
import feedparser
from datetime import datetime, timezone
import html
import sys

# Customize feeds here
FEEDS = [
    "https://ai.googleblog.com/atom.xml",
    "https://www.reddit.com/r/MachineLearning/.rss",
    "https://www.theverge.com/rss/index.xml",  # general tech, often AI stories
    # Add or remove feeds as you like
]

README = "README.md"
START = "<!-- NEWS_START -->"
END = "<!-- NEWS_END -->"
MAX_ITEMS = 7  # total headlines to include

def fetch_items():
    items = []
    for url in FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in (feed.entries or [])[:5]:
                title = html.unescape(entry.get("title", "No title"))
                link = entry.get("link", "")
                published = entry.get("published", entry.get("updated", ""))
                items.append((title, link, published))
        except Exception as e:
            print(f"Failed to fetch {url}: {e}", file=sys.stderr)
    # dedupe by link, preserve order
    seen = set()
    dedup = []
    for t, l, p in items:
        if l in seen:
            continue
        seen.add(l)
        dedup.append((t, l, p))
        if len(dedup) >= MAX_ITEMS:
            break
    return dedup

def compose_md(items):
    if not items:
        return "**Latest AI headlines will appear here — updated daily.**"
    lines = []
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines.append(f"**Updated:** {now}\n")
    for title, link, published in items:
        # show date if available
        pub_str = f" ({published})" if published else ""
        lines.append(f"- [{title}]({link}){pub_str}")
    lines.append("\n*Sources: curated from multiple tech/AI feeds*")
    return "\n".join(lines)

def replace_block(content, new_md):
    if START in content and END in content:
        pre, rest = content.split(START, 1)
        _, post = rest.split(END, 1)
        return pre + START + "\n" + new_md + "\n" + END + post
    else:
        # markers missing, append at top
        return START + "\n" + new_md + "\n" + END + "\n" + content

def main():
    items = fetch_items()
    new_md = compose_md(items)
    with open(README, "r", encoding="utf-8") as f:
        content = f.read()
    new_content = replace_block(content, new_md)
    if new_content != content:
        with open(README, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("README updated with latest headlines.")
    else:
        print("No changes detected — README remains unchanged.")

if __name__ == "__main__":
    main()
