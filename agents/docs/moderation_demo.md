# Demo 6 — `moderation_demo.py` (Content Moderation Assistant)

## What it does

A moderation agent for the fictional "Lumio" smart-lamp community forum. It
classifies incoming user comments as **ALLOW / BLOCK**. The flagged sample comments
live in the **INPUT span content**, which is exactly what the content classifiers scan.

Flow per sample:
1. `handle()` (WORKFLOW span) takes a comment.
2. `moderate()` (AGENT span) calls OpenAI `gpt-4o-mini` to classify it.
3. It runs through `SAMPLES` — two clean, one hateful, one NSFW.

### Embedded signals
- **Hate Speech (classifier)** — one sample comment is hostile toward a group.
- **NSFW Content (classifier)** — one sample comment is sexually suggestive.

> The flagged strings are deliberately **mild moderation test fixtures** — enough to
> trip the classifiers without being gratuitous.

## Earlier code (the simple version)

A single moderation agent: `handle()` → `moderate()` → return the model's decision.
That's all that's needed to put the flagged comment text into an input span so the
**Hate Speech** and **NSFW** classifiers fire.

```python
@span(kind="AGENT", name="moderator", role="Content Moderator",
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
```

## The change / update (verification hardening)

A more robust version was layered on top:
- **`run_moderation_api()`** (TOOL span) — cross-checks each comment against the
  OpenAI Moderation API.
- **`senior_review()`** (AGENT span, `gpt-4o`) — escalation reviewer invoked only when
  the primary moderator and the Moderation API **disagree**, producing the final
  binding decision.
- **Structured output** — a strict `MODERATION_SCHEMA` (decision / reasoning /
  flagged_categories).
- **`run_benchmark()`** — verifies structured output + guardrails against known
  borderline/illicit `BENCHMARK_SAMPLES`.

### Effect on signals
The core **Hate Speech / NSFW classifier** signals come purely from the flagged
sample text in the input spans — present in **both** versions. The hardening adds an
extra TOOL span, an escalation AGENT span, and a benchmark pass, but isn't required
for the two target classifiers to fire.

> Note: the script has since been **reverted to the simple single-agent version** for
> demo purposes (no Moderation API cross-check, no senior escalation, no benchmark).
