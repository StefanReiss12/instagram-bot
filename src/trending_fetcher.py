"""
Busca as notícias mais quentes de IA do dia em fontes top globais.
"""
import feedparser
from datetime import datetime, timezone, timedelta

FEEDS = [
    ("TechCrunch AI",       "https://techcrunch.com/category/artificial-intelligence/feed/"),
    ("The Verge AI",        "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml"),
    ("VentureBeat AI",      "https://venturebeat.com/category/ai/feed/"),
    ("MIT Tech Review",     "https://www.technologyreview.com/feed/"),
    ("Ars Technica",        "https://feeds.arstechnica.com/arstechnica/technology-lab"),
    ("Reuters Tech",        "https://feeds.reuters.com/reuters/technologyNews"),
    ("BBC Tech",            "http://feeds.bbci.co.uk/news/technology/rss.xml"),
    ("Wired AI",            "https://www.wired.com/feed/tag/artificial-intelligence/latest/rss"),
    ("ZDNET AI",            "https://www.zdnet.com/topic/artificial-intelligence/rss.xml"),
    ("AI News",             "https://artificialintelligence-news.com/feed/"),
]


def fetch_trending(max_items: int = 20) -> str:
    """Retorna as principais notícias de IA do dia com data e fonte."""
    headlines = []
    today     = datetime.now(timezone.utc)
    cutoff    = today - timedelta(days=3)   # últimos 3 dias

    for source, url in FEEDS:
        try:
            feed = feedparser.parse(url)
            count = 0
            for entry in feed.entries:
                if count >= 3:
                    break
                title   = entry.get("title", "").strip()
                summary = entry.get("summary", "")[:250].strip()
                if not title:
                    continue

                # Tenta pegar a data de publicação
                pub_date = ""
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    try:
                        dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                        pub_date = dt.strftime("%d/%m/%Y")
                    except Exception:
                        pass

                # Filtra palavras-chave de IA (para feeds mistos como Reuters/BBC)
                combined = (title + " " + summary).lower()
                ai_keywords = ["ai", "artificial intelligence", "openai", "anthropic",
                               "google", "deepmind", "llm", "gpt", "claude", "gemini",
                               "machine learning", "neural", "generative", "chatbot",
                               "automation", "robot", "language model", "midjourney",
                               "stable diffusion", "copilot", "ia ", "inteligência"]
                if source in ("Reuters Tech", "BBC Tech"):
                    if not any(kw in combined for kw in ai_keywords):
                        continue

                date_str = f" [{pub_date}]" if pub_date else ""
                headlines.append(f"[{source}]{date_str} {title} — {summary}")
                count += 1

        except Exception:
            continue

    if not headlines:
        return (
            "Feeds indisponíveis no momento. Use seu conhecimento sobre as notícias "
            f"mais recentes de IA Generativa até {datetime.now().strftime('%d/%m/%Y')}."
        )

    return "\n".join(headlines[:max_items])
