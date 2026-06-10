import os

from dotenv import load_dotenv
import neatlogs

load_dotenv()

neatlogs.init(api_key=os.environ["NEATLOGS_API_KEY"], workflow_name="my-first-app", debug=True)
from openai import OpenAI

client = neatlogs.wrap(OpenAI())

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "What is the capital of France?"}],
)
print(response.choices[0].message.content)

neatlogs.flush()
neatlogs.shutdown()
