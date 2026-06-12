# Hermes is not in pyproject.toml — it pins requests==2.33.0, which conflicts
# with this project. Install ad-hoc in a separate venv when needed:
#   poetry run pip install "git+https://github.com/NousResearch/hermes-agent.git"

import os
from pathlib import Path

from dotenv import load_dotenv
import neatlogs
from run_agent import AIAgent

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

neatlogs.init(
    api_key=os.environ["NEATLOGS_API_KEY"],
    endpoint=os.environ.get("NEATLOGS_ENDPOINT", "http://localhost:4100"),
    workflow_name="hermes-demo",
    instrumentations=["hermes", "openai"],
)

agent = neatlogs.wrap(AIAgent(model="openai/gpt-4o-mini", max_iterations=4))

result = agent.run_conversation(
    "Explain distributed tracing in one paragraph."
)
print(result)

neatlogs.flush()
neatlogs.shutdown()
