"""
Database models for agent state persistence.
"""

import uuid
from sqlalchemy import Column, String, JSON, DateTime, func, Text, Integer, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.db import Base

class AgentState(Base):
    """
    Model for storing agent state in PostgreSQL.
    Replaces Firestore document storage for agent state.
    """
    __tablename__ = "agent_states"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String, nullable=False, index=True)
    user_identifier = Column(String, nullable=False, index=True)
    state_key = Column(String, nullable=False)
    state_data = Column(JSON, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Composite unique constraint to ensure one state per agent/user/key combination
    __table_args__ = (
        UniqueConstraint('agent_id', 'user_identifier', 'state_key', name='uix_agent_user_key'),
    )

    def __repr__(self):
        return f"<AgentState(id={self.id}, agent_id={self.agent_id}, user_identifier={self.user_identifier}, state_key={self.state_key})>"


class AgentTask(Base):
    """
    Model for storing agent task information.
    """
    __tablename__ = "agent_tasks"

    id = Column(String, primary_key=True, index=True)
    agent_id = Column(String, nullable=False, index=True)
    user_identifier = Column(String, nullable=False, index=True)
    task_type = Column(String, nullable=False)
    status = Column(String, nullable=False)
    input_data = Column(JSON, nullable=True)
    result_data = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<AgentTask(id={self.id}, agent_id={self.agent_id}, task_type={self.task_type}, status={self.status})>"
