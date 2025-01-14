from typing import Literal
from pydantic import BaseModel


class TypeOfQuestioning(BaseModel):
    type: Literal[
        "open",
        "probing",
        "hypothetical",
        "reflective",
        "leading",
        "closing",
        "deflective",
    ]


class NextAction(BaseModel):
    next_action: Literal["ask_question", "move_on", "end_conversation"]
