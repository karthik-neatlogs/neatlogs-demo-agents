"""Demo 8 — Heavy report generator (large input + long output).

Summarizes a very large document into a long report in a single LLM call. The
call is deliberately big and slow so the corresponding neatlogs conditions fire.

Targets these neatlogs detections:
- Slow LLM Response (condition, > 10s)    : huge input + long output -> slow call
- Expensive LLM Call (condition, > $0.50) : ~60k input tokens on a premium model

WARNING: running this costs real money (~$0.60+ per run).

Add HEAVY_REPORT_NEATLOGS_API_KEY to .env before running.
"""

import neatlogs
import os
import time
from dotenv import load_dotenv
load_dotenv()
from neatlogs import span

neatlogs.init(
    api_key=os.environ["HEAVY_REPORT_NEATLOGS_API_KEY"],
    workflow_name="heavy-report-agent",
    instrumentations=["openai"],
)

# Import instrumented libraries AFTER init()
from openai import OpenAI

client = OpenAI()

MODEL = "gpt-4-turbo"
APPROX_INPUT_TOKENS = 60_000
CHARS_PER_TOKEN = 4

PARAGRAPH = (
    "The quarterly operations review covers supply chain status, regional sales "
    "performance, customer support volume, product reliability metrics, and the "
    "roadmap for the upcoming release cycle across all teams and territories. "
)
BIG_DOCUMENT = PARAGRAPH * (APPROX_INPUT_TOKENS * CHARS_PER_TOKEN // len(PARAGRAPH))


@span(kind="CHAIN", name="generate_report")
def generate_report(document):
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an analyst. Write a thorough, well-structured "
                    "multi-section report summarizing the document below."
                ),
            },
            {"role": "user", "content": document},
        ],
        max_tokens=3000,
    )
    return resp.choices[0].message.content


@span(kind="WORKFLOW", name="report_run")
def run(document):
    return generate_report(document)


def main():
    print(f"Summarizing ~{APPROX_INPUT_TOKENS} input tokens in a single {MODEL} call...")
    start = time.perf_counter()
    report = run(BIG_DOCUMENT)
    elapsed = time.perf_counter() - start
    print(f"\nCompleted in {elapsed:.1f}s")
    print("\n=== REPORT (truncated) ===")
    print(report[:1000])


main()
neatlogs.flush()
neatlogs.shutdown()
