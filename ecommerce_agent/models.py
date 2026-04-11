from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"


class ChatResponse(BaseModel):
    reply: str
    intent: Optional[str] = None
    order_id: Optional[str] = None
    resolved: bool = False
    session_id: str
