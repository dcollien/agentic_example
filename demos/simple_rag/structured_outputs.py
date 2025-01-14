from pydantic import BaseModel


class Excerpts(BaseModel):
    excerpts: list[str]
