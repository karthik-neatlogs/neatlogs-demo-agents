import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.genai.errors import ClientError
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


async def run_with_retry(
    runner,
    user_id: str,
    session_id: str,
    new_message,
    max_retries: int = 5,
    initial_backoff: float = 1.0,
    backoff_multiplier: float = 2.0,
    max_backoff: float = 60.0,
):
    """
    Run the agent with exponential backoff retry logic for 429 RESOURCE_EXHAUSTED errors.
    
    Args:
        runner: The wrapped Runner instance
        user_id: User identifier
        session_id: Session identifier
        new_message: The message content to send
        max_retries: Maximum number of retry attempts (default: 5)
        initial_backoff: Initial backoff delay in seconds (default: 1.0)
        backoff_multiplier: Multiplier for exponential backoff (default: 2.0)
        max_backoff: Maximum backoff delay in seconds (default: 60.0)
    
    Yields:
        Events from the runner
    """
    attempt = 0
    backoff = initial_backoff
    
    while attempt <= max_retries:
        try:
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=new_message,
            ):
                yield event
            return
        except ClientError as e:
            if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
                attempt += 1
                if attempt > max_retries:
                    print(f"[ERROR] Max retries ({max_retries}) exceeded for 429 RESOURCE_EXHAUSTED")
                    raise
                
                wait_time = min(backoff, max_backoff)
                print(f"[RETRY] Attempt {attempt}/{max_retries} - Got 429 RESOURCE_EXHAUSTED, retrying in {wait_time:.2f}s...")
                await asyncio.sleep(wait_time)
                backoff *= backoff_multiplier
            else:
                raise
        except Exception as e:
            print(f"[ERROR] Unexpected error: {type(e).__name__}: {e}")
            raise


async def main() -> None:
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID)
    content = types.Content(
        role="user",
        parts=[types.Part(text="In one sentence, what is Google ADK?")],
    )

    async for event in run_with_retry(
        runner=runner,
        user_id=USER_ID,
        session_id=session.id,
        new_message=content,
    ):
        if event.is_final_response():
            print(event.content.parts[0].text)


asyncio.run(main())

neatlogs.flush()
neatlogs.shutdown()
