from pydantic import BaseModel


class AgentInput(BaseModel):
    query: str
    config: dict

