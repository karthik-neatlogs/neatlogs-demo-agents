# Demo 7 — `flaky_api_agent.py` (Agent Calling a Flaky External API)

## What it does

An agent that answers stock questions for the fictional "Lumio" store by calling an
external **inventory service**. The service fails in different ways across scenarios,
producing **ERROR spans** and error text that matches the rate-limit pattern.

Flow per scenario:
1. `handle()` (WORKFLOW span) takes a question + a `scenario`.
2. `answer()` (AGENT span) calls `inventory_lookup()` (TOOL span), then asks
   `gpt-4o-mini` to phrase the answer.
3. It runs through 4 `SCENARIOS`: `ok`, `rate_limit`, `server_error`, `timeout`.

### Embedded signals
- **Execution Failed** (condition, `status=ERROR`) — the tool span raises uncaught on
  the failing scenarios → ERROR span.
- **Rate Limited** (regex: `429` / `rate_limit_error` / `quota exceeded` / `throttled`)
  — the `rate_limit` scenario raises an error whose message contains those tokens.

## Earlier code (the simple version)

The tool just **raised directly** on each failing scenario — no retry, no circuit
breaker, no graceful catch — so every failure cleanly produced an ERROR span:

```python
@span(kind="TOOL", name="inventory.lookup", tool_name="inventory.lookup")
def inventory_lookup(scenario):
    time.sleep(0.2)
    if scenario == "rate_limit":
        raise RuntimeError("rate_limit_error (HTTP 429): quota exceeded - request was throttled")
    if scenario == "server_error":
        raise RuntimeError("HTTP 500: internal server error from inventory service")
    if scenario == "timeout":
        raise TimeoutError("inventory service did not respond within 5s")
    return {"in_stock": 42}
```

`answer()` called the tool directly, so the exception propagated up through the spans
(TOOL → AGENT → WORKFLOW), and `main()` only caught it for clean console printing.

## The change / update (resilience hardening)

A more robust version was layered on top:
- **Retry with backoff** — `RETRY_BACKOFF_SECONDS = [1, 2, 4]` for retryable errors (429/500).
- **Circuit breaker** — `CircuitBreaker` opens after 3 failures to prevent retry storms.
- **Request timeout** — `INVENTORY_REQUEST_TIMEOUT = 5`.
- **Graceful agent fallback** — `answer()` catches the exception and returns a polite
  "inventory service temporarily unavailable" message.

### Effect on signals
The TOOL span still raises on terminal failure, so **Execution Failed** and **Rate
Limited** still fire — but the retry/circuit-breaker/graceful-catch layer makes the
behavior more production-like (and the AGENT/WORKFLOW spans no longer error because
the agent swallows the exception).

> Note: the script has since been **reverted to the simple version** for demo purposes
> (direct raises, no retry, no circuit breaker, no graceful fallback), so every failing
> scenario reliably produces clean ERROR spans.
