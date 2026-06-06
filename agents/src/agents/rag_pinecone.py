"""Demo 2 — Knowledge-base RAG over Pinecone for the "Lumio" product.

Pipeline per query: embed -> retrieve (Pinecone) -> build context -> answer.

Embedded signals (for neatlogs detections):
- Bad retrieval   : off-topic query returns weak matches            -> classifier
- NO_CONTEXT_FOUND: answer marker when top score is below threshold -> regex
- Token spike     : a query stuffs all docs into the context        -> token condition
- Latency         : the embedding step sleeps a random amount       -> latency condition

Index: neatlogs-testing (1536 dims) · model: text-embedding-3-small.
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
    api_key=os.environ["RAG_DEMO_NEATLOGS_API_KEY"],
    workflow_name="rag-knowledge-base",
    instrumentations=["openai"],
)

# Import instrumented libraries AFTER init()
from openai import OpenAI
from pinecone import Pinecone
from agents.data.knowledge_base import DOCUMENTS

client = OpenAI()
pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
index = pc.Index("neatlogs-testing")

EMBED_MODEL = "text-embedding-3-small"
SCORE_THRESHOLD = 0.30


@span(kind="EMBEDDING", name="embed_text")
def embed(text):
    # Simulate a slow embedding service (latency signal).
    time.sleep(random.uniform(0.2, 3.0))
    resp = client.embeddings.create(model=EMBED_MODEL, input=text)
    return resp.data[0].embedding


@span(kind="EMBEDDING", name="seed_index")
def seed():
    """Embed and upsert the knowledge base once (idempotent by id)."""
    stats = index.describe_index_stats()
    if stats.get("total_vector_count", 0) >= len(DOCUMENTS):
        print("Index already seeded, skipping.")
        return
    vectors = []
    for doc in DOCUMENTS:
        vectors.append({
            "id": doc["id"],
            "values": embed(doc["text"]),
            "metadata": {"title": doc["title"], "text": doc["text"]},
        })
    index.upsert(vectors=vectors)
    print(f"Seeded {len(vectors)} documents.")


@span(kind="RETRIEVER", name="retrieve")
def retrieve(query, top_k=3):
    vec = embed(query)
    res = index.query(vector=vec, top_k=top_k, include_metadata=True)
    return res.get("matches", [])


@span(kind="CHAIN", name="build_context")
def build_context(matches, stuff_all=False):
    if stuff_all:
        # Token-spike signal: ignore retrieval, stuff the whole KB in.
        return "\n\n".join(d["text"] for d in DOCUMENTS)
    return "\n\n".join(m["metadata"]["text"] for m in matches)


@span(kind="WORKFLOW", name="rag_query")
def answer(query, stuff_all=False):
    matches = retrieve(query)
    top_score = matches[0]["score"] if matches else 0.0

    # Weak retrieval -> emit a marker the regex detection can catch.
    if top_score < SCORE_THRESHOLD:
        return f"NO_CONTEXT_FOUND — could not find a relevant Lumio doc for: {query}"

    context = build_context(matches, stuff_all=stuff_all)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Answer using ONLY the Lumio context below. "
                                          "If the context does not cover it, say so."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
        ],
    )
    return resp.choices[0].message.content


QUERIES = [
    ("How do I set up Lumio for the first time?", False),   # good retrieval
    ("Does the Lumio Pro have a battery?", False),          # good retrieval
    ("What is the warranty period?", True),                 # token spike (stuff all)
    ("Who won the 2022 FIFA World Cup?", False),            # off-topic -> NO_CONTEXT_FOUND / classifier
]


def main():
    seed()
    for query, stuff_all in QUERIES:
        print(f"\n=== {query} (stuff_all={stuff_all}) ===")
        print(answer(query, stuff_all=stuff_all))


main()
neatlogs.flush()
neatlogs.shutdown()
