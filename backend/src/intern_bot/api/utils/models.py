from pydantic import BaseModel


class Configurable(BaseModel):
    thread_id: str

class Config(BaseModel):
    configurable: Configurable

class AgentInput(BaseModel):
    query: str
    config: Config


