"""Seed the Pinecone index with the knowledge base.

Embeds each document with text-embedding-3-small (1536 dims) and upserts it
into the `neatlogs-testing` index. Run once before using rag_pinecone.py:

    poetry run python src/agents/seed_pinecone.py
"""

import os
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
from pinecone import Pinecone
from agents.data.knowledge_base import DOCUMENTS

INDEX_NAME = "neatlogs-testing"
EMBED_MODEL = "text-embedding-3-small"

client = OpenAI()
pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
index = pc.Index(INDEX_NAME)


def embed(text):
    resp = client.embeddings.create(model=EMBED_MODEL, input=text)
    return resp.data[0].embedding


def main():
    vectors = []
    for doc in DOCUMENTS:
        print(f"Embedding {doc['id']} — {doc['title']}")
        vectors.append({
            "id": doc["id"],
            "values": embed(doc["text"]),
            "metadata": {"title": doc["title"], "text": doc["text"]},
        })

    index.upsert(vectors=vectors)
    print(f"\nUpserted {len(vectors)} documents into '{INDEX_NAME}'.")
    print(index.describe_index_stats())


main()
