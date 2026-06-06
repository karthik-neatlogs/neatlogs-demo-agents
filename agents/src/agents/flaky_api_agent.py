"""Demo 7 — Agent calling a flaky external API.

The agent answers a request that requires an external service call. The service
fails in different ways across scenarios, producing ERROR spans and error text
that matches the rate-limit pattern.

Targets these neatlogs detections:
- Execution Failed (condition, status=ERROR) : tool spans raise uncaught -> ERROR
- Rate Limited (regex: 429 / rate_limit_error / quota exceeded / throttled) :
  one scenario raises an error whose message contains those tokens

Add FLAKY_API_NEATLOGS_API_KEY to .env before running.
"""

import neatlogs
import os
import time
from dotenv import load_dotenv
load_dotenv()
from neatlogs import span

neatlogs.init(
    api_key=os.environ["FLAKY_API_NEATLOGS_API_KEY"],
    workflow_name="flaky-api-agent",
    instrumentations=["openai"],
)

# Import instrumented libraries AFTER init()
from openai import OpenAI

client = OpenAI()


@span(kind="TOOL", name="inventory.lookup", tool_name="inventory.lookup")
def inventory_lookup(scenario):
    # Mock downstream inventory call — raises directly on each failure scenario.
    time.sleep(0.2)
    if scenario == "rate_limit":
        raise RuntimeError(
            "rate_limit_error (HTTP 429): quota exceeded - request was throttled"
        )
    if scenario == "server_error":
        raise RuntimeError("HTTP 500: internal server error from inventory service")
    if scenario == "timeout":
        raise TimeoutError("inventory service did not respond within 5s")
    return {"in_stock": 42}


@span(kind="AGENT", name="inventory_agent",
      role="Inventory Assistant",
      goal="Answer stock questions using the inventory service")
def answer(question, scenario):
    stock = inventory_lookup(scenario)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You answer inventory questions for the Lumio store."},
            {"role": "user", "content": f"{question}\n\nInventory data: {stock}"},
        ],
    )
    return resp.choices[0].message.content


@span(kind="WORKFLOW", name="inventory_request")
def handle(question, scenario):
    return answer(question, scenario)


SCENARIOS = [
    ("How many Lumio Pro lamps are in stock?", "ok"),            # success
    ("Do you have the Sage finish available?", "rate_limit"),    # -> Rate Limited + Execution Failed
    ("Is the standard Lumio in stock?", "server_error"),         # -> Execution Failed
    ("Can I order 10 units today?", "timeout"),                  # -> Execution Failed
]


def main():
    for question, scenario in SCENARIOS:
        print(f"\n=== {question} (scenario={scenario}) ===")
        try:
            print(handle(question, scenario))
        except Exception as e:
            print(f"[ERROR] {e}")


main()
neatlogs.flush()
neatlogs.shutdown()
