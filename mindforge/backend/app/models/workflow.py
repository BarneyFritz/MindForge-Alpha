from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey, JSON
from app.models.base import Base

class WorkflowSession(Base):
    __tablename__ = "workflow_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), nullable=True)
    input_prompt: Mapped[str] = mapped_column(String(4000))
    result: Mapped[dict | None] = mapped_column(JSON, nullable=True)