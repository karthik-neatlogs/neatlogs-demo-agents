import os
from pathlib import Path
from typing import Annotated, Literal, Sequence, TypedDict

from dotenv import load_dotenv
import neatlogs
from neatlogs import SystemPromptTemplate, UserPromptTemplate, span, trace

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

neatlogs.init(
    api_key=os.environ["NEATLOGS_API_KEY"],
    endpoint=os.environ.get("NEATLOGS_ENDPOINT", "https://staging-cloud.neatlogs.com"),
    workflow_name="customer-support",
    instrumentations=["langchain"],
)

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages


class WorkflowState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    intent: str


llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

supervisor_prompt = SystemPromptTemplate([{
    "role": "system",
    "content": "Classify the intent of the user's query as either 'knowledge' or 'orders'. Respond with only the intent word.",
}])
supervisor_user_prompt = UserPromptTemplate([{"role": "user", "content": "Query: {{query}}"}])


def supervisor(state: WorkflowState) -> dict:
    query = state["messages"][-1].content
    with trace(
        "classify_intent",
        kind="LLM",
        system_prompt_template=supervisor_prompt,
        user_prompt_template=supervisor_user_prompt,
    ):
        msgs = supervisor_prompt.compile() + supervisor_user_prompt.compile(query=query)
        response = llm.invoke(msgs)
    intent = "orders" if "order" in response.content.lower() else "knowledge"
    return {"intent": intent, "messages": [response]}


knowledge_prompt = SystemPromptTemplate([{
    "role": "system",
    "content": "You are a helpful assistant. Answer the user's question about our products and policies.",
}])
knowledge_user_prompt = UserPromptTemplate([{"role": "user", "content": "{{question}}"}])


def knowledge_agent(state: WorkflowState) -> dict:
    question = state["messages"][0].content
    with trace(
        "answer_question",
        kind="LLM",
        system_prompt_template=knowledge_prompt,
        user_prompt_template=knowledge_user_prompt,
    ):
        msgs = knowledge_prompt.compile() + knowledge_user_prompt.compile(question=question)
        response = llm.invoke(msgs)
    return {"messages": [response]}


orders_prompt = SystemPromptTemplate([{
    "role": "system",
    "content": "You are an order management assistant. Help the user with their order inquiry.",
}])
orders_user_prompt = UserPromptTemplate([{"role": "user", "content": "{{question}}"}])


def orders_agent(state: WorkflowState) -> dict:
    question = state["messages"][0].content
    with trace(
        "handle_order",
        kind="LLM",
        system_prompt_template=orders_prompt,
        user_prompt_template=orders_user_prompt,
    ):
        msgs = orders_prompt.compile() + orders_user_prompt.compile(question=question)
        response = llm.invoke(msgs)
    return {"messages": [response]}


def route(state: WorkflowState) -> Literal["knowledge_agent", "orders_agent"]:
    return "orders_agent" if state["intent"] == "orders" else "knowledge_agent"


graph = StateGraph(WorkflowState)
graph.add_node("supervisor", supervisor)
graph.add_node("knowledge_agent", knowledge_agent)
graph.add_node("orders_agent", orders_agent)
graph.add_edge(START, "supervisor")
graph.add_conditional_edges("supervisor", route)
graph.add_edge("knowledge_agent", END)
graph.add_edge("orders_agent", END)
app = graph.compile()


@span(kind="WORKFLOW", name="support_request")
def run_workflow(query: str) -> str:
    result = app.invoke({
        "messages": [HumanMessage(content=query)],
        "intent": "",
    })
    return result["messages"][-1].content


print(run_workflow("What is your return policy?"))

neatlogs.flush()
neatlogs.shutdown()
