from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from .db import Base


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    persistent_memory = Column(Boolean, default=False)
    owner_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    sessions = relationship("Session", back_populates="project")


class ModelConfig(Base):
    __tablename__ = "models"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    model_id = Column(String, nullable=False)
    temperature = Column(Integer, default=1)
    max_tokens = Column(Integer, default=512)
    enable_expand = Column(Boolean, default=True)
    enable_critique = Column(Boolean, default=True)
    enable_synth = Column(Boolean, default=True)
    owner_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    seed = Column(Text, nullable=False)
    context = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="sessions")
    ideas = relationship("Idea", back_populates="session", cascade="all, delete-orphan")
    critiques = relationship("Critique", back_populates="session", cascade="all, delete-orphan")
    summaries = relationship("Summary", back_populates="session", cascade="all, delete-orphan")


class Idea(Base):
    __tablename__ = "ideas"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    model_ref = Column(String, nullable=False)
    text = Column(Text, nullable=False)

    session = relationship("Session", back_populates="ideas")


class Critique(Base):
    __tablename__ = "critiques"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    idea_id = Column(Integer, ForeignKey("ideas.id"))
    critic_ref = Column(String, nullable=False)
    text = Column(Text, nullable=False)

    session = relationship("Session", back_populates="critiques")


class Summary(Base):
    __tablename__ = "summary"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    model_ref = Column(String, nullable=False)
    markdown = Column(Text, nullable=False)

    session = relationship("Session", back_populates="summaries")


class Export(Base):
    __tablename__ = "exports"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    type = Column(String, nullable=False)
    path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)