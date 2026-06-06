"""Demo 3 — Multi-step research agent with a tool loop.

The agent issues several "web_search" tool calls, then summarizes. Some runs
loop many times and one search fails before a retry succeeds.

Embedded signals (for neatlogs detections):
- High tool count : a topic triggers many search iterations  -> tool_call_count condition
- Tool error+retry: web_search fails once, then retries      -> error / fix
- Expensive run   : a large summary prompt drives up tokens   -> cost / token condition
- Latency         : each search sleeps a random amount        -> latency condition

Swap NEATLOGS_API_KEY in .env to this script's own project before running.
"""

import neatlogs
import os
import time
import random
from dotenv import load_dotenv
load_dotenv()
from neatlogs import span

neatlogs.init(
    api_key=os.environ["RESEARCH_AGENT_NEATLOGS_API_KEY"],
    workflow_name="research-agent",
    instrumentations=["openai"],
)

# Import instrumented libraries AFTER init()
from openai import OpenAI

client = OpenAI()

# Fake search corpus — returns canned snippets per query word.
FAKE_RESULTS = [
    "Industry reports show steady growth in this area over the last five years.",
    "Analysts cite improved efficiency and lower costs as key drivers.",
    "A competing study found mixed results depending on the region.",
    "Recent advances suggest the trend will continue into next year.",
    "Critics argue the data is incomplete and more research is needed.",
]

MAX_SEARCH_ATTEMPTS = 4


@span(kind="TOOL", name="web_search", tool_name="search.web")
def web_search(query, attempt=1):
    time.sleep(random.uniform(0.2, 2.5))
    # Fail on the first attempt for one in three searches, then succeed on retry.
    if attempt == 1 and random.random() < 0.33:
        raise ConnectionError(f"search backend timed out for: {query}")
    return random.sample(FAKE_RESULTS, k=3)


def search_with_retry(query):
    # Immediate sequential retries, no backoff (pre-fix behavior).
    for attempt in range(1, MAX_SEARCH_ATTEMPTS + 1):
        try:
            return web_search(query, attempt=attempt)
        except ConnectionError as e:
            print(f"[retry] attempt {attempt} failed: {e}")
            if attempt >= MAX_SEARCH_ATTEMPTS:
                raise


@span(kind="AGENT", name="researcher",
      role="Research Analyst",
      goal="Gather evidence and write a short briefing on the topic")
def research(topic, depth):
    findings = []
    # depth controls how many tool calls happen (high depth -> many calls).
    for i in range(depth):
        sub_query = f"{topic} — aspect {i + 1}"
        findings.extend(search_with_retry(sub_query))

    notes = "\n".join(f"- {f}" for f in findings)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a research analyst. Write a concise briefing "
                                          "from the notes provided."},
            {"role": "user", "content": f"Topic: {topic}\n\nNotes:\n{notes}"},
        ],
    )
    return resp.choices[0].message.content


@span(kind="WORKFLOW", name="research_task")
def run_research(topic, depth):
    return research(topic, depth)


TASKS = [
    ("the future of remote work", 2),          # shallow
    ("electric vehicle battery trends", 8),    # deep -> many tool calls + cost
    ("trends in home lighting design", 3),     # medium
]


def main():
    for topic, depth in TASKS:
        print(f"\n=== {topic} (depth={depth}) ===")
        print(run_research(topic, depth))


main()
neatlogs.flush()
neatlogs.shutdown()
