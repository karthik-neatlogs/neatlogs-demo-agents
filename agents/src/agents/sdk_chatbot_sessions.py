import os
from pathlib import Path

from dotenv import load_dotenv
import neatlogs
from neatlogs import SystemPromptTemplate, UserPromptTemplate, span, trace

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

neatlogs.init(
    api_key=os.environ["NEATLOGS_API_KEY"],
    endpoint=os.environ.get("NEATLOGS_ENDPOINT", "https://staging-cloud.neatlogs.com"),
    workflow_name="support-chatbot",
    instrumentations=["openai"],
    auto_session=True,
)

from openai import OpenAI

client = OpenAI()

system_tpl = SystemPromptTemplate([
    {
        "role": "system",
        "content": "You are a helpful support assistant. Use the conversation history to give consistent answers.",
    },
])
user_tpl = UserPromptTemplate([
    {"role": "user", "content": "{{message}}"},
])


@span(kind="AGENT", name="chatbot_turn")
def chatbot_turn(message: str, history: list) -> str:
    with trace(
        "respond",
        kind="LLM",
        system_prompt_template=system_tpl,
        user_prompt_template=user_tpl,
    ):
        system_msgs = system_tpl.compile()
        user_msgs = user_tpl.compile(message=message)
        messages = system_msgs + history + user_msgs

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )
    return response.choices[0].message.content


# Scripted multi-turn demo (replace with input() loop for interactive use).
turns = [
    "What is your return policy?",
    "How long do I have to return an item?",
    "Do I need the original packaging?",
]

history = []
for user_input in turns:
    print(f"You: {user_input}")
    reply = chatbot_turn(user_input, history)
    print(f"Bot: {reply}\n")

    history.append({"role": "user", "content": user_input})
    history.append({"role": "assistant", "content": reply})

neatlogs.flush()
neatlogs.shutdown()
