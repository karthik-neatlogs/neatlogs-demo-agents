import os

from dotenv import load_dotenv
import neatlogs
from openai import OpenAI

load_dotenv()

neatlogs.init(api_key=os.environ["NEATLOGS_API_KEY"], endpoint=os.environ.get("NEATLOGS_ENDPOINT", "http://localhost:4100"), workflow_name="openai-demo")

client = neatlogs.wrap(OpenAI())

resp = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "In one sentence, what is OpenAI?"}],
)
print(resp.choices[0].message.content)

neatlogs.flush()
neatlogs.shutdown()
