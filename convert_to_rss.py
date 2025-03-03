import requests
import json
import os
import re
from datetime import datetime
from feedgen.feed import FeedGenerator

MAIN_JSON_URL = "https://launchercontent.mojang.com/v2/javaPatchNotes.json"
RSS_FEED_FILE = "index.xml"

def fetch_json(url):
    """Fetch JSON data from URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return {}

def generate_minecraft_url(version, release_type):
    """Generate the correct Minecraft.net article URL based on version and type."""
    base_url = "https://www.minecraft.net/en-us/article/"
    
    if re.search("^[0-9][0-9]w[0-9][0-9][a-z]$", version) != None:
        return f"{base_url}minecraft-snapshot-{version.lower()}"
    elif "pre" in version:
        return f"{base_url}minecraft-{version.replace('.', '-').replace('-pre', '-pre-release-')}"
    elif "rc" in version:
        return f"{base_url}minecraft-{version.replace('.', '-').replace('-rc', '-release-candidate-')}"
    else:  # Full releases
        return f"{base_url}minecraft-java-edition-{version.replace('.', '-')}"

# Fetch main JSON data
data = fetch_json(MAIN_JSON_URL)

# Create RSS feed
fg = FeedGenerator()
fg.title("Minecraft Java Patch Notes")
fg.link(href="https://jeeukko.github.io/minecraft-news-feed/index.xml", rel='self', type='application/rss+xml')
fg.description("Latest Minecraft Java Edition patch notes")
fg.language("en")

# Process entries
for entry in data.get("entries", []):
    version = entry["version"]
    title = entry["title"]
    date = entry["date"]
    release_type = entry["type"]  # snapshot, pre-release, rc, release
    short_text = entry["shortText"]

    article_url = generate_minecraft_url(version, release_type)
    post_date = datetime.fromisoformat(date.replace("Z", "+00:00"))

    # Create RSS item
    fe = fg.add_entry(order='append')
    fe.title(title)
    fe.link(href=article_url)
    fe.guid(guid=article_url, permalink=True)
    fe.pubDate(post_date)
    fe.description(short_text)

# Save RSS feed
fg.rss_file(RSS_FEED_FILE, pretty=True)

print("RSS feed updated successfully.")
