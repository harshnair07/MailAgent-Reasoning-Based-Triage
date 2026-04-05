from pydantic import Field, BaseModel
from typing import Optional

# 1. Define the AI's "Eyes"
class EmailObservation(BaseModel):
    subject: str = Field(..., description="The subject line of the email.")
    email_text: str = Field(..., description="The body content of the email.")
    sender: str = Field(..., description="The sender's email address.")
    is_vip: bool = Field(..., description="True if this is a high-priority contact.")
    
    # ADD THESE TWO FIELDS:
    reward: float = Field(default=0.0, description="The reward from the previous action.")
    done: bool = Field(default=False, description="Whether the episode is finished.")

# 2. Define the AI's "Hands"
class EmailAction(BaseModel):
    folder: str = Field(..., description="The chosen folder: Urgent, Work, Social, or Spam.")
    reasoning: str = Field(..., description="The agent's logic for this classification.")