# Demo 1 — `support_bot.py` (Lumio Support Chatbot)

## What it does

A customer support chatbot for the fictional "Lumio" smart desk lamp.

Flow per scenario:
1. `handle()` (WORKFLOW span) takes a user message + optional `order_id`.
2. `answer()` (AGENT span) optionally calls `lookup_order()` (TOOL span) against a
   fake in-memory CRM, builds an order-context string, then calls OpenAI
   `gpt-4o-mini` to reply.
3. It runs 5 `SCENARIOS` designed to trigger different neatlogs detections.

### Embedded signals
- **PII** — the CRM record carries a customer **name + email** that flows into the prompt/output.
- **Latency** — `lookup_order()` sleeps a random `0.3–4.0s` to simulate a slow CRM call.
- **Off-topic** — the "pasta recipe" scenario is unrelated to support, for the classifier.
- **Error / fix** — order `9999` isn't in the CRM (see below).

## Earlier code (the bug we wanted to surface)

`lookup_order()` **raised an exception** on an unknown order id:

```python
@span(kind="TOOL", name="lookup_order", tool_name="crm.lookup_order")
def lookup_order(order_id):
    time.sleep(random.uniform(0.3, 4.0))
    if order_id not in ORDERS:
        raise ValueError(f"Order {order_id} not found in CRM")
    return ORDERS[order_id]
```

Because the exception propagated up through the `@span`-decorated function, the span
was marked **`status = ERROR`**. So support_bot generated real **ERROR-status spans**
→ lit up the **"Execution Failed" detection** and the **fixes** workflow for the
`9999` scenario.

## The change / update (the graceful "fix")

`lookup_order()` was changed to **return an error string** instead of raising:

```python
@span(kind="TOOL", name="lookup_order", tool_name="crm.lookup_order")
def lookup_order(order_id):
    time.sleep(random.uniform(0.3, 4.0))
    if order_id not in ORDERS:
        return f"Order {order_id} not found in CRM. Please check the ID and try again."
    return ORDERS[order_id]
```

`answer()` was updated to handle both shapes — if the result is a `dict` it's a real
order; otherwise it treats the string as a tool-error message and instructs the model
to relay it cleanly (so it doesn't hallucinate order details).

### Effect on signals
| | Unknown order behavior | Error / "fixes" signal |
|---|---|---|
| **Before** | raised exception → **ERROR span** | ✅ shows in Execution Failed / fixes |
| **After**  | returned string → no ERROR span    | ❌ none |

After this edit, support_bot still produces **PII, latency, and off-topic** signals,
but **no longer produces error/fix signals**. The error/"fixes" demos shifted to
`flaky_api_agent.py` and `research_agent.py`.
