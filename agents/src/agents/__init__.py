"""Agents package.

Loads environment variables from the project's .env and initializes the
neatlogs SDK so traces are exported automatically on import.
"""

import os

import neatlogs
from dotenv import load_dotenv

# Load variables from the project-root .env (searches upward from CWD).
load_dotenv()

# neatlogs.init() reads NEATLOGS_API_KEY from the environment when api_key
# is not passed explicitly.
neatlogs.init(
    api_key=os.getenv("NEATLOGS_API_KEY"),
    workflow_name="agents",
)
