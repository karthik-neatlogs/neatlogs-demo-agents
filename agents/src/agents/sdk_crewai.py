import os
from pathlib import Path

from dotenv import load_dotenv

os.environ.setdefault(
    "CREWAI_STORAGE_DIR",
    str(Path(__file__).resolve().parents[2] / ".crewai"),
)

import neatlogs
from crewai import Agent, Crew, LLM, Task

load_dotenv()

neatlogs.init(
    api_key=os.environ["NEATLOGS_API_KEY"],
    endpoint=os.environ.get("NEATLOGS_ENDPOINT", "http://localhost:4100"),
    workflow_name="crewai-demo",
    instrumentations=["crewai", "openai"],
)

llm = LLM(model="gpt-4o")

researcher = Agent(
    role="Researcher",
    goal="Answer questions in one sentence",
    backstory="You give concise, accurate answers.",
    llm=llm,
    verbose=False,
)

task = Task(
    description="In one sentence, what is CrewAI?",
    expected_output="A single concise sentence.",
    agent=researcher,
)

crew = neatlogs.wrap(Crew(agents=[researcher], tasks=[task], verbose=False))
result = crew.kickoff()
print(result)

neatlogs.flush()
neatlogs.shutdown()
