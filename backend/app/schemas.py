from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class UserOut(BaseModel):
    id: int
    email: str
    name: Optional[str] = None
    picture: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    persistent_memory: bool = False

class ProjectOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    persistent_memory: bool
    created_at: datetime
    class Config:
        from_attributes = True

class SessionCreate(BaseModel):
    project_id: int
    prompt: str
    selected_connectors: List[str] = Field(default_factory=list)
    rounds: int = 2
    lead_connector: str = "openai"

class MessageOut(BaseModel):
    id: int
    connector: str
    role: str
    round_index: int
    content: str
    model_used: Optional[str] = None
    confidence: Optional[float] = None
    created_at: datetime
    class Config:
        from_attributes = True

class SessionOut(BaseModel):
    id: int
    project_id: int
    prompt: str
    selected_connectors: List[str]
    rounds: int
    lead_connector: str
    status: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageOut] = []
    class Config:
        from_attributes = True

class ExportPayload(BaseModel):
    session_id: int
    markdown: Optional[str] = None
    json: Optional[dict] = None
    mindmap: Optional[str] = None