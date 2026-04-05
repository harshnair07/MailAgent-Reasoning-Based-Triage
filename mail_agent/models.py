from pydantic import Field
from openenv import Action, Observation

# 1. Define the AI's "Eyes" (What it sees)
class EmailObservation(Observation):
    email_text: str = Field(..., description="The subject line and body of the email.")
    sender: str = Field(..., description="The sender's email address.")
    is_vip: bool = Field(..., description="True if this is a high-priority contact.")

# 2. Define the AI's "Hands" (What it does)
class EmailAction(Action):
    folder: str = Field(..., description="The chosen folder: Urgent, Work, Social, or Spam.")
    reasoning: str = Field(..., description="The agent's logic for this classification.")