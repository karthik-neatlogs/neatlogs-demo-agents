import os

from dotenv import load_dotenv
import neatlogs
from strands import Agent
from strands.models.openai import OpenAIModel

load_dotenv()

neatlogs.init(api_key=os.environ["NEATLOGS_API_KEY"], workflow_name="strands-demo")

model = OpenAIModel(
    client_args={"api_key": os.environ["OPENAI_API_KEY"]},
    model_id="gpt-4o",
)
agent = Agent(model=model)
neatlogs.strands_hooks(agent)

print(agent("In one sentence, what is Strands?"))

neatlogs.flush()
neatlogs.shutdown()
