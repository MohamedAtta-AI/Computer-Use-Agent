from pydantic import BaseModel

class Message(BaseModel):
    role: str       # "user" | "assistant" | "tool"
    content: str

class SessionCreateResponse(BaseModel):
    session_id: str

class Ack(BaseModel):
    status: str = "queued"
