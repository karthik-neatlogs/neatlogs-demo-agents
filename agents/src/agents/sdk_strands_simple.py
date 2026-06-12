import os

from dotenv import load_dotenv
import neatlogs
from strands import Agent
from strands.models.openai import OpenAIModel

load_dotenv()

neatlogs.init(api_key=os.environ["NEATLOGS_API_KEY"], endpoint=os.environ.get("NEATLOGS_ENDPOINT", "http://localhost:4100"), workflow_name="strands-demo")

agent = Agent(
    model=OpenAIModel(
        client_args={"api_key": os.environ["OPENAI_API_KEY"]},
        model_id="gpt-4o-mini",
    )
)
neatlogs.strands_hooks(agent)

print(agent("In one sentence, what is Strands?"))

neatlogs.flush()
neatlogs.shutdown()
