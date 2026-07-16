import requests
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


def generate_minecraft_url(title):
    """Generate the Minecraft.net article URL from the article title."""
    slug = (
        title.lower()
        .replace(":", "")
        .replace(".", "-")
        .replace(" ", "-")
    )

    # Collapse multiple consecutive dashes
    slug = re.sub(r"-+", "-", slug)

    return f"https://www.minecraft.net/en-us/article/{slug}"


# Fetch main JSON data
data = fetch_json(MAIN_JSON_URL)

# Create RSS feed
fg = FeedGenerator()
fg.title("Minecraft Java Patch Notes")
fg.link(
    href="https://jeeukko.github.io/minecraft-news-feed/index.xml",
    rel="self",
    type="application/rss+xml",
)
fg.description("Latest Minecraft Java Edition patch notes")
fg.language("en")

# Process entries
for entry in data.get("entries", []):
    title = entry["title"]
    date = entry["date"]
    short_text = entry["shortText"]

    article_url = generate_minecraft_url(title)
    post_date = datetime.fromisoformat(date.replace("Z", "+00:00"))

    # Create RSS item
    fe = fg.add_entry(order="append")
    fe.title(title)
    fe.link(href=article_url)
    fe.guid(guid=article_url, permalink=True)
    fe.pubDate(post_date)
    fe.description(short_text)

# Save RSS feed
fg.rss_file(RSS_FEED_FILE, pretty=True)

print("RSS feed updated successfully.")
