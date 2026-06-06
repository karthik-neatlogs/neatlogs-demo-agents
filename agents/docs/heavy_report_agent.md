# Demo 8 — `heavy_report_agent.py` (Heavy Report Generator)

## What it does

Summarizes a very large document into a long report. The point of the demo is to be
**slow and expensive** so the corresponding neatlogs conditions fire.

Flow:
1. `run()` (WORKFLOW span) takes a big document.
2. `generate_report()` (CHAIN span) makes one large LLM call to produce a long report.

### Targeted detections
- **Slow LLM Response** (condition, > 10s) — a huge input + long output makes a single
  call take a long time.
- **Expensive LLM Call** (condition, > $0.50) — ~60k input tokens on a premium model
  drives real cost to **~$0.60+ per run**.

> ⚠️ Running this costs real money (~$0.60+ per run).

## Earlier code (the simple, deliberately heavy version)

A single giant LLM call on `gpt-4-turbo` with ~60k input tokens and a 3k-token output:

```python
MODEL = "gpt-4-turbo"
APPROX_INPUT_TOKENS = 60_000

@span(kind="CHAIN", name="generate_report")
def generate_report(document):
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are an analyst. Write a thorough, "
             "well-structured multi-section report summarizing the document below."},
            {"role": "user", "content": document},
        ],
        max_tokens=3000,
    )
    return resp.choices[0].message.content
```

This single big call is what reliably trips **Slow LLM Response** (> 10s) and
**Expensive LLM Call** (> $0.50).

## The change / update (cost & latency optimization)

A map-reduce version was layered on top to *reduce* cost and latency:
- **Chunking** — `chunk_document()` splits the input into ~8k-token overlapping chunks.
- **Cheap map step** — each chunk summarized in parallel with `gpt-4o-mini`
  (`summarize_chunk`, CHAIN span) via a `ThreadPoolExecutor`.
- **Premium reduce step** — only the final synthesis uses `gpt-4o`
  (`synthesize_report`, CHAIN span).
- Lower input footprint (`APPROX_INPUT_TOKENS = 38_000`).

### Effect on signals
The optimization is the *opposite* of what this demo wants — it brings latency and cost
**down**, which would stop the Slow/Expensive conditions from firing. It's useful as a
"here's the fix" reference, but not for reproducing the detections.

> Note: the script has since been **reverted to the single heavy `gpt-4-turbo` call**
> (~60k input tokens, 3k output) so it reliably trips Slow LLM Response and Expensive
> LLM Call.
