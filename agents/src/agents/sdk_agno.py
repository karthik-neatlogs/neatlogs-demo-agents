import os

from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
import neatlogs

load_dotenv()

neatlogs.init(api_key=os.environ["NEATLOGS_API_KEY"], endpoint=os.environ.get("NEATLOGS_ENDPOINT", "http://localhost:4100"), workflow_name="agno-demo")

agent = neatlogs.wrap(Agent(model=OpenAIChat(id="gpt-4o")))

print(agent.run("In one sentence, what is Agno?").content)

neatlogs.flush()
neatlogs.shutdown()
