import os

from dotenv import load_dotenv
import neatlogs

load_dotenv()

neatlogs.init(
    api_key=os.environ["NEATLOGS_API_KEY"],
    workflow_name="langchain-demo",
    instrumentations=["langchain"],
)

# Import LangChain AFTER init() so it's patched.
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o")

print(llm.invoke("In one sentence, what is LangChain?").content)

neatlogs.flush()
neatlogs.shutdown()
