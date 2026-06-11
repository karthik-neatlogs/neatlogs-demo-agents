import os

from dotenv import load_dotenv
import neatlogs
from pydantic_ai import Agent

load_dotenv()

neatlogs.init(api_key=os.environ["NEATLOGS_API_KEY"], workflow_name="pydantic-ai-demo")

agent = neatlogs.wrap(Agent("openai:gpt-4o", system_prompt="Be concise."))

result = agent.run_sync("In one sentence, what is Pydantic AI?")
print(result.output)

neatlogs.flush()
neatlogs.shutdown()
