import os
from pathlib import Path

from dotenv import load_dotenv

os.environ.setdefault(
    "DSPY_CACHEDIR",
    str(Path(__file__).resolve().parents[2] / ".dspy_cache"),
)

import dspy
import neatlogs

load_dotenv()

neatlogs.init(api_key=os.environ["NEATLOGS_API_KEY"], workflow_name="dspy-demo")

dspy.configure(lm=dspy.LM("openai/gpt-4o"))


class QA(dspy.Module):
    def __init__(self):
        super().__init__()
        self.answer = dspy.Predict("question -> answer")

    def forward(self, question: str):
        return self.answer(question=question)


program = neatlogs.wrap(QA())

result = program(question="In one sentence, what is DSPy?")
print(result.answer)

neatlogs.flush()
neatlogs.shutdown()
