import feedparser
import urllib.parse

def get_news_headlines(company_name: str, max_headlines: int = 8):
    """
    Fetch recent news headlines for a company using Google News RSS.
    No API key required.
    """
    query = urllib.parse.quote(f"{company_name} stock")
    url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"

    feed = feedparser.parse(url)
    headlines = []
    for entry in feed.entries[:max_headlines]:
        headlines.append(entry.title)

    return headlines


if __name__ == "__main__":
    result = get_news_headlines("Tata Consultancy Services")
    for h in result:
        print("-", h)