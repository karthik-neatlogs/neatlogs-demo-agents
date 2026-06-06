"""Demo 5 — Structured data extractor (messy text -> JSON).

Asks the model to return JSON for each input, then parses it.

Embedded signals (for neatlogs detections):
- JSON parse error : a tricky input yields malformed JSON          -> error / fix
- Regex marker     : on failure the output carries '"status": "failed"' -> regex
- Token / latency  : a large blob input is slow and token-heavy    -> condition

Swap NEATLOGS_API_KEY in .env to this script's own project before running.
"""

import neatlogs
import os
import json
from dotenv import load_dotenv
load_dotenv()
from neatlogs import span

neatlogs.init(
    api_key=os.environ["DATA_EXTRACTOR_NEATLOGS_API_KEY"],
    workflow_name="data-extractor",
    instrumentations=["openai"],
)

# Import instrumented libraries AFTER init()
from openai import OpenAI

client = OpenAI()


@span(kind="CHAIN", name="extract_json")
def extract_json(text, strict_json=True):
    instruction = ("Extract the person's name, email, and company as JSON with keys "
                   "name, email, company. Return ONLY valid JSON.")
    if not strict_json:
        # Nudge the model toward prose so json.loads fails -> error signal.
        instruction = ("Describe the person's name, email, and company in a short "
                       "sentence, then optionally include some JSON.")
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": instruction},
            {"role": "user", "content": text},
        ],
    )
    return resp.choices[0].message.content


@span(kind="WORKFLOW", name="extraction_run")
def run(text, strict_json=True):
    raw = extract_json(text, strict_json=strict_json)
    try:
        parsed = json.loads(raw)
        return {"status": "ok", "data": parsed}
    except json.JSONDecodeError as e:
        # Marker string for the regex detection.
        return {"status": "failed", "error": str(e), "raw": raw}


BIG_BLOB = "Contact record: " + ("noise " * 800) + \
    "Name: Elena Park, email elena.park@example.com, works at Northwind Labs."

INPUTS = [
    ("Reach out to Sam Carter, sam.carter@example.com, from Acme Inc.", True),   # clean JSON
    ("Jordan Blake (jordan.blake@example.com) is at Globex.", True),             # clean JSON
    ("Our contact is Riya from BlueSky, riya@bluesky.io.", False),               # prose -> parse error
    (BIG_BLOB, True),                                                            # large -> token/latency
]


def main():
    for text, strict in INPUTS:
        print(f"\n=== {text[:60]}... (strict={strict}) ===")
        result = run(text, strict_json=strict)
        print(json.dumps(result, indent=2))


main()
neatlogs.flush()
neatlogs.shutdown()
