from __future__ import annotations

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class TaskStatus(str, Enum):
    """Enum for possible task statuses."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Task(BaseModel):
    """
    Represents a single instance of an orchestrated task or workflow run.
    Used to track the state and progress of tasks managed by the Orchestrator/WorkflowManager.
    """
    taskId: str = Field(..., description="Unique identifier for the task instance.")
    userId: Optional[str] = Field(None, description="ID of the user who initiated the task.")
    goal: Optional[str] = Field(None, description="The high-level goal or prompt that initiated the task.")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Current status of the task.")
    current_stage: Optional[str] = Field(None, description="Identifier for the current stage or step the task is executing.")
    stage_outputs: Dict[str, Any] = Field(default_factory=dict, description="Dictionary to store outputs from completed stages.")
    result: Optional[Dict[str, Any]] = Field(None, description="Final result of the task upon completion.")
    error_message: Optional[str] = Field(None, description="Error message if the task failed.")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the task was created.")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the task was last updated.")

    class Config:
        use_enum_values = True # Ensure enum values are used when serializing
        # Example configuration if needed, e.g., for ORM mode if integrating later
        # orm_mode = True
        pass

# Example Usage (for reference):
# task_data = {
#     "taskId": "task-12345",
#     "userId": "user-abc",
#     "goal": "Generate income stream for 'sustainable gardening'",
#     "status": TaskStatus.RUNNING,
#     "current_stage": "stage_1_market_research",
#     "stage_outputs": {},
#     "created_at": datetime.utcnow(),
#     "updated_at": datetime.utcnow()
# }
# task_instance = Task(**task_data)
# print(task_instance.json())