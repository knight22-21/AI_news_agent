import os
from dotenv import load_dotenv

# Load .env variables into environment
load_dotenv()

from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool
from newsapi import NewsApiClient

newsapi = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))  # Use env variable for key

@tool
def fetch_ai_news():
    """Fetch and summarize recent LLM, RAG, or AI Agent-related news articles."""

    def fetch_articles(domains):
        response = newsapi.get_everything(
            q="LLM OR large language models OR retrieval augmented generation OR RAG OR AI agents OR autonomous agents",
            domains=domains,
            language="en",
            sort_by="publishedAt",
            page_size=5,
        )
        return response.get("articles", [])

    def format_articles(articles):
        summaries = []
        for art in articles[:3]:  # Only top 3
            title = art.get("title", "No title")
            desc = art.get("description", "")
            url = art.get("url", "")
            summaries.append(f"{title}\nSummary: {desc}\nURL: {url}")
        return "\n\n".join(summaries)

    preferred = "artificialintelligence-news.com"
    fallback = "techcrunch.com,venturebeat.com,theverge.com,wired.com,technologyreview.com"

    articles = fetch_articles(preferred)
    if not articles:
        articles = fetch_articles(fallback)

    if not articles:
        return "No recent news found related to LLMs, RAG, or agents."

    return format_articles(articles)

llm = LLM(
    model="ollama/mistral",
    base_url="http://localhost:11434",
)

news_agent = Agent(
    role="AI News Researcher",
    goal="Summarize real-time AI news on LLMs, RAG, or AI agents.",
    backstory="You're a highly skilled AI news analyst...",
    tools=[fetch_ai_news],
    llm=llm,    
    verbose=True,
)

news_task = Task(
    description=(
        "Use the 'fetch_ai_news' tool to retrieve a batch of recent AI news articles "
        "related to LLMs, RAG, and AI Agents. From these, choose the top most important topics. "
        "Provide the topic, summary and no URLs\n\n"
    ),
    expected_output=(
        "A structured plain-text summary in the specified format of the top 3 news topics "
    ),
    agent=news_agent,
)

summary_agent = Agent(
    role="AI Summary Refiner",
    goal="Polish and format AI news into a clear, structured summary without asterisks or URLs.",
    backstory="You're an expert communicator. Your job is to take raw summaries and refine them into clean, professional news briefs. Use hyphens for bullets, bold or clearly marked topic titles, and remove URLs.",
    tools=[],
    llm=llm,
    verbose=True,
)


summary_task = Task(
    description=(
        "Take the summarized news from the researcher agent. "
        "Format it into a plain-text summary suitable for users. "
        "Use this structure:\n\n"
        "Title \n"
        "- Bullet point 1\n"
        "- Bullet point 2\n"
        "(Optionally a 3rd point)\n\n"
        "Do not include any URLs or markdown symbols like asterisks. Ensure clarity, readability, and proper grammar."
    ),
    expected_output="Clean, user-ready plain-text summary of top AI news topics with no URLs or symbols.",
    agent=summary_agent,
)


crew = Crew(
    agents=[news_agent, summary_agent],
    tasks=[news_task, summary_task],
    process=Process.sequential,  
    verbose=True,
)

