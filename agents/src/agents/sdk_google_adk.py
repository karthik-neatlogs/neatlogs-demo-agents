import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import neatlogs

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

if not os.environ.get("GOOGLE_API_KEY") and os.environ.get("GEMINI_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]

APP_NAME = "google-adk-demo"
USER_ID = "demo-user"

neatlogs.init(api_key=os.environ["NEATLOGS_API_KEY"], workflow_name="google-adk-demo")

agent = LlmAgent(
    name="assistant",
    model="gemini-2.0-flash",
    instruction="Be concise.",
)

session_service = InMemorySessionService()
runner = neatlogs.wrap(
    Runner(agent=agent, app_name=APP_NAME, session_service=session_service)
)


async def main() -> None:
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID)
    content = types.Content(
        role="user",
        parts=[types.Part(text="In one sentence, what is Google ADK?")],
    )

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session.id,
        new_message=content,
    ):
        if event.is_final_response():
            print(event.content.parts[0].text)


asyncio.run(main())

neatlogs.flush()
neatlogs.shutdown()
