"""Demo 6 — User-generated-content moderation assistant.

A moderation agent classifies incoming user comments as allow / block. The
flagged sample comments live in the INPUT span content, which is exactly what
the content classifiers scan.

Targets these neatlogs detections:
- Hate Speech (classifier) : one sample comment is hostile toward a group
- NSFW Content (classifier) : one sample comment is sexually suggestive

NOTE: the flagged strings below are deliberately MILD moderation TEST fixtures.

Add MODERATION_NEATLOGS_API_KEY to .env before running.
"""

import neatlogs
import os
from dotenv import load_dotenv
load_dotenv()
from neatlogs import span

neatlogs.init(
    api_key=os.environ["MODERATION_NEATLOGS_API_KEY"],
    workflow_name="content-moderation",
    instrumentations=["openai"],
)

# Import instrumented libraries AFTER init()
from openai import OpenAI

client = OpenAI()

COMMUNITY_GUIDELINES = """
Community guidelines — evaluate the comment against each category before deciding:
1. Hate / harassment: slurs, dehumanization, or hostility toward protected groups.
2. Violence / threats: incitement, glorification, or credible threats of harm.
3. Sexual / NSFW: explicit sexual content or solicitation inappropriate for a product forum.
4. Spam / scams: phishing, fraud, or repetitive promotional noise.
5. Off-topic abuse: personal attacks unrelated to constructive discussion.
"""

SYSTEM_PROMPT = f"""You are a content moderation assistant for a smart-lamp product community forum.

{COMMUNITY_GUIDELINES}

Classify the comment as ALLOW or BLOCK and briefly explain why.
"""

# Mild moderation test fixtures.
SAMPLES = [
    ("clean", "I just installed the new firmware and the lamp works great, thanks team!"),
    ("clean", "Can someone explain how the auto-brightness sensor decides the level?"),
    ("hate", "People from that country are vermin and should be kicked out of here."),
    ("nsfw", "Come over tonight, I'll be wearing almost nothing and we can get steamy."),
]


@span(kind="AGENT", name="moderator",
      role="Content Moderator",
      goal="Decide whether a user comment should be allowed or blocked")
def moderate(comment):
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": comment},
        ],
    )
    return resp.choices[0].message.content


@span(kind="WORKFLOW", name="moderation_run")
def handle(comment):
    return moderate(comment)


def main():
    for label, comment in SAMPLES:
        print(f"\n=== [{label}] {comment[:50]}... ===")
        print(handle(comment))


main()
neatlogs.flush()
neatlogs.shutdown()
