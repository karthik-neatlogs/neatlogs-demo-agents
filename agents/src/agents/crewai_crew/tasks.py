import neatlogs
from crewai import Task


def research_task(agent, topic: str) -> Task:
    description = f"Research the following topic thoroughly: {topic}"
    expected_output = "A detailed summary of findings with key facts and sources."
    task = Task(description=description, expected_output=expected_output, agent=agent)
    neatlogs.register_crewai_task(
        task,
        neatlogs.UserPromptTemplate(description + "\n\n" + expected_output),
    )
    return task


def write_report_task(agent, context: list) -> Task:
    description = "Using the research findings, write a concise 3-paragraph report."
    expected_output = "A polished report ready for publication."
    task = Task(
        description=description,
        expected_output=expected_output,
        agent=agent,
        context=context,
    )
    neatlogs.register_crewai_task(
        task,
        neatlogs.UserPromptTemplate(description + "\n\n" + expected_output),
    )
    return task
