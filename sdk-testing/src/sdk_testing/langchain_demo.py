import os
from pathlib import Path

from dotenv import load_dotenv
import neatlogs

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

neatlogs.init(
    api_key=os.environ["NEATLOGS_API_KEY"],
    endpoint=os.environ.get("NEATLOGS_ENDPOINT", "http://localhost:4100"),
    workflow_name="langchain-demo",
    instrumentations=["langchain"],
)

# Import LangChain AFTER init() so it's patched.
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o")

print(llm.invoke("In one sentence, what is LangChain?").content)

neatlogs.flush()
neatlogs.shutdown()
