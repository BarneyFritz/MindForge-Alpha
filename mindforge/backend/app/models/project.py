from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey
from app.models.base import Base

class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)