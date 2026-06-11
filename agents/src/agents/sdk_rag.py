import json
import os
from pathlib import Path

from dotenv import load_dotenv
import neatlogs
from neatlogs import SystemPromptTemplate, UserPromptTemplate, span, trace

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

neatlogs.init(
    api_key=os.environ["NEATLOGS_API_KEY"],
    endpoint=os.environ.get("NEATLOGS_ENDPOINT", "https://staging-cloud.neatlogs.com"),
    workflow_name="rag-api",
    instrumentations=["openai"],
)

from openai import OpenAI

from data.knowledge_base import DOCUMENTS

# Simple in-memory store for the demo (no Chroma/Pinecone required).
MOCK_DOCS = [
    {
        "id": doc["id"],
        "content": doc["text"],
        "title": doc["title"],
    }
    for doc in DOCUMENTS
]


class MockVectorStore:
    def search(self, query: str, k: int = 5) -> list[dict]:
        query_words = set(query.lower().split())
        scored = []
        for doc in MOCK_DOCS:
            text_words = set(doc["content"].lower().split())
            score = len(query_words & text_words)
            scored.append({**doc, "score": score})
        scored.sort(key=lambda d: d["score"], reverse=True)
        return scored[:k]


class MockReranker:
    def rerank(self, query: str, docs: list, top_n: int = 3) -> list:
        query_words = set(query.lower().split())
        reranked = sorted(
            docs,
            key=lambda d: len(query_words & set(d["content"].lower().split())),
            reverse=True,
        )
        return reranked[:top_n]


my_vector_store = MockVectorStore()
my_reranker = MockReranker()

rag_template = SystemPromptTemplate([
    {
        "role": "system",
        "content": "Answer the question using only the provided context.\n\nContext:\n{{context}}",
    },
])
user_template = UserPromptTemplate([
    {"role": "user", "content": "{{question}}"},
])


def retrieve(query: str, top_k: int = 5) -> list:
    with trace("retrieve", kind="RETRIEVER") as span:
        span.set_attribute("neatlogs.retrieval.query", query)
        span.set_attribute("neatlogs.retrieval.top_k", top_k)
        docs = my_vector_store.search(query, k=top_k)
        span.set_attribute("neatlogs.retrieval.documents", json.dumps(docs))
    return docs


def rerank(query: str, docs: list, top_n: int = 3) -> list:
    with trace("rerank", kind="RERANKER") as span:
        span.set_attribute("neatlogs.reranker.query", query)
        span.set_attribute("neatlogs.reranker.top_k", top_n)
        span.set_attribute("neatlogs.reranker.input_documents", json.dumps(docs))
        reranked = my_reranker.rerank(query, docs, top_n=top_n)
        span.set_attribute("neatlogs.reranker.output_documents", json.dumps(reranked))
    return reranked


@span(kind="CHAIN", name="rag_pipeline")
def rag_pipeline(question: str) -> str:
    docs = retrieve(question, top_k=5)
    reranked = rerank(question, docs, top_n=3)
    context = "\n\n".join(doc["content"] for doc in reranked)

    with trace(
        "generate",
        kind="LLM",
        system_prompt_template=rag_template,
        user_prompt_template=user_template,
    ):
        system_msgs = rag_template.compile(context=context)
        user_msgs = user_template.compile(question=question)
        response = OpenAI().chat.completions.create(
            model="gpt-4o",
            messages=system_msgs + user_msgs,
        )
        return response.choices[0].message.content


answer = rag_pipeline("What is the return policy for electronics?")
print(answer)

neatlogs.flush()
neatlogs.shutdown()
