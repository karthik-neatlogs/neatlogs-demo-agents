"""Demo 4 — Meeting-transcript -> task assignment agent.

Reads a meeting transcript and produces task assignments, one per line in the
form "ASSIGNED TO: <name> — <task>".

Embedded signals (for neatlogs detections):
- Regex      : output lines contain "ASSIGNED TO:"                  -> regex
- PII        : transcripts include participant names + emails        -> PII detection
- Token spike: one transcript is very long                           -> token condition
- Off-scope  : a casual transcript yields out-of-scope "tasks"       -> classifier

Swap NEATLOGS_API_KEY in .env to this script's own project before running.
"""

import neatlogs
import os
from dotenv import load_dotenv
load_dotenv()
from neatlogs import span

neatlogs.init(
    api_key=os.environ["MEETING_TASKS_NEATLOGS_API_KEY"],
    workflow_name="meeting-task-agent",
    instrumentations=["openai"],
)

# Import instrumented libraries AFTER init()
from openai import OpenAI

client = OpenAI()

SHORT_TRANSCRIPT = """\
Sprint planning, attendees: Priya Nair (priya.nair@example.com), Tom Becker (tom.becker@example.com).
Priya: We need the login bug fixed before Friday.
Tom: I'll take the login bug. Priya, can you update the onboarding docs?
Priya: Sure, I'll handle the docs and review Tom's PR.
"""

# A deliberately long transcript to drive up token usage.
LONG_TRANSCRIPT = "Quarterly review, attendees: Sara Diaz (sara.diaz@example.com), Mike Ross (mike.ross@example.com).\n" + (
    "Sara: Let's go over each open item in detail and assign owners.\n"
    "Mike: Agreed, there is a lot to cover this quarter across every team.\n"
) * 60 + "Sara: Mike, please prepare the budget summary. Mike: Sara, you take the hiring plan.\n"

CASUAL_TRANSCRIPT = """\
Lunch chat, attendees: two coworkers.
A: That new taco place downtown is amazing, we should go Friday.
B: Totally. Also did you watch the game last night?
A: Yeah, wild ending. Anyway, back to work I guess.
"""


@span(kind="CHAIN", name="extract_tasks")
def extract_tasks(transcript):
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Extract action items from the meeting transcript. "
                                          "Output one line per task in the exact format: "
                                          "'ASSIGNED TO: <name> — <task>'. If there are no real "
                                          "work tasks, still output your best guess in that format."},
            {"role": "user", "content": transcript},
        ],
    )
    return resp.choices[0].message.content


@span(kind="WORKFLOW", name="meeting_run")
def process(transcript):
    return extract_tasks(transcript)


MEETINGS = [
    ("sprint", SHORT_TRANSCRIPT),     # normal + PII + regex
    ("quarterly", LONG_TRANSCRIPT),   # token spike + PII + regex
    ("lunch", CASUAL_TRANSCRIPT),     # off-scope -> classifier
]


def main():
    for label, transcript in MEETINGS:
        print(f"\n=== {label} ===")
        print(process(transcript))


main()
neatlogs.flush()
neatlogs.shutdown()
