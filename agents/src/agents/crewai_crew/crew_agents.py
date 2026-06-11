import neatlogs
from crewai import Agent, LLM


def research_agent() -> Agent:
    system_tpl = neatlogs.SystemPromptTemplate(
        "You are a research specialist. Find accurate, up-to-date information on the given topic."
    )
    return Agent(
        role="Researcher",
        goal="Research and summarize information accurately",
        backstory=str(system_tpl.template),
        llm=neatlogs.bind_templates(
            LLM(model="openai/gpt-4o"),
            system_tpl,
        ),
        allow_delegation=False,
        verbose=False,
    )


def writer_agent() -> Agent:
    system_tpl = neatlogs.SystemPromptTemplate(
        "You are a professional writer. Produce clear, concise reports from research findings."
    )
    return Agent(
        role="Writer",
        goal="Write clear reports from research findings",
        backstory=str(system_tpl.template),
        llm=neatlogs.bind_templates(
            LLM(model="openai/gpt-4o"),
            system_tpl,
        ),
        allow_delegation=False,
        verbose=False,
    )
