import os
from dotenv import load_dotenv  # <-- Add this

# Load .env variables into environment
load_dotenv()
import os
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from newsapi import NewsApiClient

newsapi = NewsApiClient(api_key=os.getenv("NEWS_API_KEY")) # Set your API key here or use env var

@tool
def fetch_ai_news():
    """Fetch and summarize recent AI-related news articles."""

    def fetch_articles(domains):
        
        response = newsapi.get_everything(
            q="AI OR artificial intelligence OR machine learning OR deep learning OR generative AI OR LLM OR NLP",
            domains=domains,
            language="en",
            sort_by="publishedAt",
            page_size=5,
        )
        return response.get("articles", [])

    def format_articles(articles):
        summaries = []
        for art in articles:
            title = art.get("title", "No title")
            source = art.get("source", {}).get("name", "Unknown source")
            desc = art.get("description", "")
            url = art.get("url", "")
            summaries.append(f"Title: {title}\nSource: {source}\nSummary: {desc}\nURL: {url}")
        return "\n\n".join(summaries)

    preferred = "artificialintelligence-news.com"
    fallback = "techcrunch.com,venturebeat.com,theverge.com,wired.com,technologyreview.com"

    articles = fetch_articles(preferred)
    if not articles:
        articles = fetch_articles(fallback)

    if not articles:
        return "No recent AI news found."

    return format_articles(articles)

llm = LLM(
    model="ollama/mistral",
    base_url="http://localhost:11434",
)

news_agent = Agent(
    role="AI News Researcher",
    goal="Summarize real-time AI news from trusted sources",
    backstory="You're a highly skilled AI news analyst...",
    tools=[fetch_ai_news],
    llm=llm,
    verbose=True,
)

news_task = Task(
    description=(
        "Use the 'fetch_ai_news' tool to retrieve the latest AI news and summarize the top 3 most impactful developments. "
        "Your summary should be insightful, markdown formatted, and concise."
    ),
    expected_output="A markdown-formatted summary of the 3 most important AI news articles today.",
    agent=news_agent,
)

crew = Crew(
    agents=[news_agent],
    tasks=[news_task],
    process=Process.sequential,
    verbose=True,
)

