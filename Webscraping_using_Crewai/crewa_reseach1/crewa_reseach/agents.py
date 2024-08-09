import os
from textwrap import dedent
from crewai import Agent
from crewai_tools import ScrapeWebsiteTool, SerperDevTool
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

# Use GPT-4
openai_llm = ChatOpenAI(api_key=os.environ.get("OPENAI_API_KEY"), model="gpt-4")

scrape_website_tool = ScrapeWebsiteTool()
search_tool = SerperDevTool()

web_researcher_agent = Agent(
    role="Web Researcher",
    goal="Your goal is to search for relevant content about the comparison between Llama 2 and Llama 3",
    tools=[scrape_website_tool, search_tool],
    backstory=dedent(
        """
        You are proficient at searching for specific topics on the web, selecting those that provide
        more value and information.
        """
    ),
    verbose=True,
    allow_delegation=False,
    llm=openai_llm
)

doppelganger_agent = Agent(
    role="LinkedIn Post Creator",
    goal="You will compare Llama 2 and Llama 3",
    backstory=dedent(
        """
        You are an expert in writing blogs.
        """
    ),
    verbose=True,
    allow_delegation=False,
    llm=openai_llm
)
