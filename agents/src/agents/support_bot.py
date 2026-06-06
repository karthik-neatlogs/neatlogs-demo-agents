"""Demo 1 — Customer support chatbot for the fictional "Lumio" smart lamp.

Embedded signals (for neatlogs detections):
- TOOL error      : lookup_order() returns an error string on unknown order id
- PII             : order context carries customer name + email    -> PII detection
- Latency         : the CRM lookup sleeps a random amount          -> latency condition
- Off-topic       : one query is unrelated to support              -> classifier

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
    api_key=os.environ["SUPPORT_BOT_NEATLOGS_API_KEY"],
    workflow_name="support-chatbot",
    instrumentations=["openai"],
)

# Import instrumented libraries AFTER init()
from openai import OpenAI

client = OpenAI()

# Fake CRM — note the PII (names + emails) that can leak into model output.
ORDERS = {
    "1001": {"status": "shipped", "customer": "Maria Gomez", "email": "maria.gomez@example.com"},
    "1002": {"status": "processing", "customer": "David Lee", "email": "david.lee@example.com"},
    "1003": {"status": "delivered", "customer": "Aisha Khan", "email": "aisha.khan@example.com"},
}


@span(kind="TOOL", name="lookup_order", tool_name="crm.lookup_order")
def lookup_order(order_id):
    # Simulate a slow CRM call (latency signal).
    time.sleep(random.uniform(0.3, 4.0))
    if order_id not in ORDERS:
        # Raise so the span is marked status=ERROR (Execution Failed / fixes signal).
        raise ValueError(f"Order {order_id} not found in CRM")
    return ORDERS[order_id]


@span(kind="AGENT", name="support_agent",
      role="Lumio Support Agent",
      goal="Resolve customer questions about Lumio lamps and their orders")
def answer(user_msg, order_id=None):
    context = ""
    if order_id:
        order = lookup_order(order_id)
        context = (f"Order {order_id}: status={order['status']}, "
                   f"customer={order['customer']}, email={order['email']}")
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a support agent for Lumio smart desk lamps. "
                                          "If order context is provided, summarize it for the customer."},
            {"role": "user", "content": f"{user_msg}\n\nOrder context: {context or 'none'}"},
        ],
    )
    return resp.choices[0].message.content


@span(kind="WORKFLOW", name="support_request")
def handle(user_msg, order_id=None):
    return answer(user_msg, order_id)


SCENARIOS = [
    ("Where is my order? Can you confirm my details?", "1001"),   # PII + latency
    ("What's the status of my order?", "1002"),                   # PII + latency
    ("My lamp won't connect to Wi-Fi, what should I do?", None),  # normal support
    ("Track my order please", "9999"),                            # unknown id -> error
    ("Can you recommend a good pasta recipe for dinner?", None),  # off-topic -> classifier
]


def main():
    for msg, order_id in SCENARIOS:
        print(f"\n=== {msg} (order={order_id}) ===")
        try:
            print(handle(msg, order_id))
        except Exception as e:
            print(f"[ERROR] {e}")


main()
neatlogs.flush()
neatlogs.shutdown()
