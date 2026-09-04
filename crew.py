import os

from dotenv import load_dotenv
from crewai import Crew, Process

from agents import build_agents
from tasks import build_tasks

load_dotenv()

REQUIRED_KEYS = ("OPENAI_API_KEY", "SERPER_API_KEY")


def run(question):
    missing = [key for key in REQUIRED_KEYS if not os.getenv(key)]
    if missing:
        raise SystemExit("Missing from .env: " + ", ".join(missing))

    researcher, analyst, writer = build_agents()
    tasks = build_tasks(question, researcher, analyst, writer)

    # Sequential, not hierarchical: each task sees only the previous task's output, so
    # the writer never has access to raw search results.
    crew = Crew(
        agents=[researcher, analyst, writer],
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
    )
    return crew.kickoff()
