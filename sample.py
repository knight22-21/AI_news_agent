import os
from dotenv import load_dotenv  # <-- Add this

# Load .env variables into environment
load_dotenv()
from newsapi import NewsApiClient

# Initialize NewsAPI client
newsapi = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))

def fetch_articles(domains):
    response = newsapi.get_everything(
        q="AI OR artificial intelligence OR machine learning OR deep learning OR generative AI OR LLM OR NLP",
        domains=domains,
        language="en",
        sort_by="publishedAt",
        page_size=5
    )
    return response.get("articles", [])

def print_articles(articles, source_desc):
    if not articles:
        print(f"No articles found from {source_desc}.\n")
        return False
    print(f"✅ Articles from {source_desc}:\n")
    for art in articles:
        print(f"- {art['title']}\n  Source: {art['source']['name']}\n  URL: {art['url']}\n")
    return True

def main():
    preferred_domain = "artificialintelligence-news.com"
    articles = fetch_articles(preferred_domain)
    if not print_articles(articles, preferred_domain):
        fallback_domains = "techcrunch.com,venturebeat.com,theverge.com,wired.com,technologyreview.com"
        articles = fetch_articles(fallback_domains)
        print_articles(articles, "fallback sources")

if __name__ == "__main__":
    main()
