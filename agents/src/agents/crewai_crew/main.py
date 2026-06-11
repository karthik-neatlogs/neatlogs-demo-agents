import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

os.environ.setdefault("CREWAI_STORAGE_DIR", str(ROOT / ".crewai"))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

import neatlogs

neatlogs.init(
    api_key=os.environ["NEATLOGS_API_KEY"],
    endpoint=os.environ.get("NEATLOGS_ENDPOINT", "https://staging-cloud.neatlogs.com"),
    workflow_name="support-crew",
    instrumentations=["crewai", "openai"],
)

from crewai import Crew

sys.path.insert(0, str(Path(__file__).resolve().parent))

from crew_agents import research_agent, writer_agent
from tasks import research_task, write_report_task


@neatlogs.span(kind="WORKFLOW", name="research_crew")
def run(topic: str) -> str:
    researcher = research_agent()
    writer = writer_agent()

    task1 = research_task(researcher, topic=topic)
    task2 = write_report_task(writer, context=[task1])

    crew = Crew(agents=[researcher, writer], tasks=[task1, task2], verbose=False)
    result = crew.kickoff()
    return result.raw if hasattr(result, "raw") else str(result)


print(run("Advances in vector database technology in 2024"))

neatlogs.flush()
neatlogs.shutdown()
