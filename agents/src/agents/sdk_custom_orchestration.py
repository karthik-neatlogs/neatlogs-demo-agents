import json
import os
from pathlib import Path

from dotenv import load_dotenv
import neatlogs
from neatlogs import SystemPromptTemplate, UserPromptTemplate, span, trace

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

neatlogs.init(
    api_key=os.environ["NEATLOGS_API_KEY"],
    endpoint=os.environ.get("NEATLOGS_ENDPOINT", "https://staging-cloud.neatlogs.com"),
    workflow_name="research-agent",
)

from openai import OpenAI

client = neatlogs.wrap(OpenAI())

system_tpl = SystemPromptTemplate([
    {
        "role": "system",
        "content": "You are a research assistant. Use available tools to answer the user's question.",
    },
])
user_tpl = UserPromptTemplate([
    {"role": "user", "content": "Question: {{question}}"},
])


@span(kind="TOOL", tool_name="web_search", description="Search the web for recent articles")
def web_search(query: str) -> list:
    return [
        {
            "title": f"Recent article about {query}",
            "snippet": (
                "Transformer architectures continue to evolve with sparse attention, "
                "mixture-of-experts scaling, and more efficient long-context models."
            ),
        }
    ]


@span(kind="AGENT", name="research_agent", role="Researcher")
def research_agent(question: str) -> str:
    messages = []

    for _ in range(5):
        with trace(
            "reason",
            kind="LLM",
            system_prompt_template=system_tpl,
            user_prompt_template=user_tpl,
        ):
            system_msgs = system_tpl.compile()
            user_msgs = user_tpl.compile(question=question)
            if not messages:
                messages = system_msgs + user_msgs

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "web_search",
                            "description": "Search the web for recent articles",
                            "parameters": {
                                "type": "object",
                                "properties": {"query": {"type": "string"}},
                                "required": ["query"],
                            },
                        },
                    }
                ],
            )

        msg = response.choices[0].message
        if not msg.tool_calls:
            return msg.content or ""

        assistant_msg = {"role": msg.role, "content": msg.content}
        if msg.tool_calls:
            assistant_msg["tool_calls"] = [
                {
                    "id": call.id,
                    "type": call.type,
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments,
                    },
                }
                for call in msg.tool_calls
            ]
        messages.append(assistant_msg)
        for call in msg.tool_calls:
            args = json.loads(call.function.arguments)
            if call.function.name == "web_search":
                result = web_search(**args)
            else:
                result = []
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(result),
            })

    return "Could not complete research."


@span(kind="WORKFLOW", name="research_workflow")
def run(question: str) -> str:
    return research_agent(question)


result = run("What are the latest advances in transformer architectures?")
print(result)

neatlogs.flush()
neatlogs.shutdown()
