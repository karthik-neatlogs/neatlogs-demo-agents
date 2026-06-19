# Hermes is not in pyproject.toml — install ad-hoc when needed:
#   poetry run pip install "git+https://github.com/NousResearch/hermes-agent.git"
#
# Hermes defaults to OpenRouter; set OPENROUTER_API_KEY in agents/.env.

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
print(result.get("final_response", result) if isinstance(result, dict) else result)

neatlogs.flush()
neatlogs.shutdown()
