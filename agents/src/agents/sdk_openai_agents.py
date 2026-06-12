import os

from dotenv import load_dotenv
from agents import Agent, Runner, add_trace_processor
import neatlogs

load_dotenv()

neatlogs.init(api_key=os.environ["NEATLOGS_API_KEY"], endpoint=os.environ.get("NEATLOGS_ENDPOINT", "http://localhost:4100"), workflow_name="openai-agents-demo")
add_trace_processor(neatlogs.openai_agents_processor())

agent = Agent(name="assistant", instructions="Be concise.")
result = Runner.run_sync(agent, "In one sentence, what is the OpenAI Agents SDK?")
print(result.final_output)

neatlogs.flush()
neatlogs.shutdown()
