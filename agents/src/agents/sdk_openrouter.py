import os
from pathlib import Path

from dotenv import load_dotenv
import neatlogs
from openrouter import OpenRouter

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

neatlogs.init(api_key=os.environ["NEATLOGS_API_KEY"], workflow_name="openrouter-demo")

client = neatlogs.wrap(OpenRouter(api_key=os.environ["OPENROUTER_API_KEY"]))

resp = client.chat.send(
    model="openai/gpt-4o-mini",
    messages=[{"role": "user", "content": "In one sentence, what is OpenRouter?"}],
    temperature=0.3,
    top_p=0.9,
    max_tokens=256,
)
print(resp.choices[0].message.content)

neatlogs.flush()
neatlogs.shutdown()
