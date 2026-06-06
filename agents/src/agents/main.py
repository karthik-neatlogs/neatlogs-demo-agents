import neatlogs
import os
from dotenv import load_dotenv
load_dotenv()
from neatlogs import span

neatlogs.init(
    api_key=os.environ["NEATLOGS_API_KEY"],       # or NEATLOGS_API_KEY env var
    # endpoint="https://staging-cloud.neatlogs.com",  # or NEATLOGS_ENDPOINT env var
    workflow_name="my-agent",
    instrumentations=["openai"],
)

# Import instrumented libraries AFTER init()
from openai import OpenAI


@span(kind="WORKFLOW", name="quickstart")
def main():
    client = OpenAI()
    return client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "What is AI?"}],
    )


main()
neatlogs.flush()
neatlogs.shutdown()