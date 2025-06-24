from crewai import Agent, Crew, LLM
from crewai_tools import SerperDevTool
import os
from datetime import date
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Now get the API key from environment
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")

# Step 1: Set up the LLM (Mistral via Ollama)
llm = LLM(model="ollama/mistral", base_url="http://localhost:11434")

# Step 2: Create search tool
search_tool = SerperDevTool()

# Step 3: Format today's date
today_str = date.today().isoformat()  # e.g., "2025-06-23"

# Step 4: Define the agent
news_agent = Agent(
    role="AI News Researcher",
    goal="Track and summarize the latest AI developments with real-time search",
    backstory="An expert in cutting-edge AI research and news, capable of identifying breaking developments.",
    tools=[search_tool],
    llm=llm
)

# Step 5: Task prompt — embed Google-style filter
task_description = (
    f"Search for breaking artificial intelligence news using this query: "
    f"'latest AI news after:{today_str}'. Only summarize news clearly published or updated today ({today_str}). "
    f"Return the top 3 developments with clear timestamps and relevant context."
)

expected_output = (
    f"A list of 3 recent AI-related news items (as of {today_str}). "
    f"Each must include: title, source or company/research lab, and a 1–2 sentence summary. "
    f"Only include stories clearly marked as from {today_str}."
)

# Step 6: Run the Crew
crew = Crew(
    agents=[news_agent],
    tasks=[{
        "agent": news_agent,
        "description": task_description,
        "expected_output": expected_output
    }]
)

if __name__ == "__main__":
    print(f"🚀 Running AI News Agent for {today_str}...\n")
    result = crew.kickoff()
    print("\n📰 AI News Summary:\n")
    print(result)
