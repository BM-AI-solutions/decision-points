"""
Database models for workflow state persistence.
"""

import uuid
from sqlalchemy import Column, String, JSON, DateTime, func, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.db import Base

class Workflow(Base):
    """
    Model for storing workflow state in PostgreSQL.
    Replaces Firestore document storage for workflow state.
    """
    __tablename__ = "workflows"

    id = Column(String, primary_key=True, index=True)  # workflow_run_id
    initial_topic = Column(String, nullable=False)
    target_url = Column(String, nullable=True)
    status = Column(String, nullable=False)
    current_step = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Store JSON data for each step's result
    market_research_result = Column(JSON, nullable=True)
    product_spec_data = Column(JSON, nullable=True)
    brand_package_data = Column(JSON, nullable=True)
    code_generation_result = Column(JSON, nullable=True)
    deployment_result = Column(JSON, nullable=True)
    marketing_result = Column(JSON, nullable=True)
    final_result = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship to workflow steps
    steps = relationship("WorkflowStep", back_populates="workflow", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Workflow(id={self.id}, status={self.status}, current_step={self.current_step})>"


class WorkflowStep(Base):
    """
    Model for storing individual workflow step details.
    """
    __tablename__ = "workflow_steps"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(String, ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False)
    step_name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    
    # Relationship to workflow
    workflow = relationship("Workflow", back_populates="steps")
    
    def __repr__(self):
        return f"<WorkflowStep(id={self.id}, workflow_id={self.workflow_id}, step_name={self.step_name}, status={self.status})>"
