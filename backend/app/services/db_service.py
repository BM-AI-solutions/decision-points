"""
Database service for agent state management.
Provides methods for storing and retrieving agent state from PostgreSQL.
"""

import json
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.models.workflow import Workflow, WorkflowStep
from app.models.agent_state import AgentState, AgentTask
from app.core.db import SessionLocal
from app.config import settings

logger = logging.getLogger(__name__)

class DatabaseService:
    """
    Service for interacting with the database for agent state management.
    """

    @staticmethod
    async def get_db_session() -> AsyncSession:
        """
        Get a database session.

        Returns:
            AsyncSession: A database session.
        """
        async with SessionLocal() as session:
            return session

    # --- Workflow Methods ---

    @staticmethod
    async def create_workflow(
        workflow_id: str,
        initial_topic: str,
        target_url: Optional[str] = None,
        status: str = "STARTING"
    ) -> Workflow:
        """
        Create a new workflow in the database.

        Args:
            workflow_id: The workflow ID.
            initial_topic: The initial topic for the workflow.
            target_url: Optional target URL for market research.
            status: The initial status of the workflow.

        Returns:
            The created workflow.
        """
        async with SessionLocal() as session:
            workflow = Workflow(
                id=workflow_id,
                initial_topic=initial_topic,
                target_url=target_url,
                status=status
            )
            session.add(workflow)
            await session.commit()
            await session.refresh(workflow)
            return workflow

    @staticmethod
    async def get_workflow(workflow_id: str) -> Optional[Workflow]:
        """
        Get a workflow by ID.

        Args:
            workflow_id: The workflow ID.

        Returns:
            The workflow, or None if not found.
        """
        async with SessionLocal() as session:
            result = await session.execute(
                select(Workflow).where(Workflow.id == workflow_id)
            )
            return result.scalars().first()

    @staticmethod
    async def update_workflow_state(
        workflow_id: str,
        state_data: Dict[str, Any]
    ) -> Optional[Workflow]:
        """
        Update a workflow's state.

        Args:
            workflow_id: The workflow ID.
            state_data: The state data to update.

        Returns:
            The updated workflow, or None if not found.
        """
        async with SessionLocal() as session:
            # Get the workflow
            result = await session.execute(
                select(Workflow).where(Workflow.id == workflow_id)
            )
            workflow = result.scalars().first()

            if not workflow:
                logger.warning(f"Workflow {workflow_id} not found for update")
                return None

            # Update the workflow with the state data
            for key, value in state_data.items():
                if hasattr(workflow, key):
                    setattr(workflow, key, value)

            # Always update last_updated
            workflow.last_updated = datetime.now()

            await session.commit()
            await session.refresh(workflow)
            return workflow

    @staticmethod
    async def create_workflow_step(
        workflow_id: str,
        step_name: str,
        status: str = "RUNNING"
    ) -> WorkflowStep:
        """
        Create a new workflow step.

        Args:
            workflow_id: The workflow ID.
            step_name: The name of the step.
            status: The initial status of the step.

        Returns:
            The created workflow step.
        """
        async with SessionLocal() as session:
            step = WorkflowStep(
                workflow_id=workflow_id,
                step_name=step_name,
                status=status
            )
            session.add(step)
            await session.commit()
            await session.refresh(step)
            return step

    @staticmethod
    async def update_workflow_step(
        step_id: int,
        status: Optional[str] = None,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        completed: bool = False
    ) -> Optional[WorkflowStep]:
        """
        Update a workflow step.

        Args:
            step_id: The step ID.
            status: The new status of the step.
            result: The result data of the step.
            error: Any error message.
            completed: Whether the step is completed.

        Returns:
            The updated workflow step, or None if not found.
        """
        async with SessionLocal() as session:
            # Get the step
            result_query = await session.execute(
                select(WorkflowStep).where(WorkflowStep.id == step_id)
            )
            step = result_query.scalars().first()

            if not step:
                logger.warning(f"Workflow step {step_id} not found for update")
                return None

            # Update the step
            if status:
                step.status = status

            if result:
                step.result = result

            if error:
                step.error = error

            if completed:
                step.completed_at = datetime.now()

            await session.commit()
            await session.refresh(step)
            return step

    # --- Agent State Methods ---

    @staticmethod
    async def get_agent_state(
        agent_id: str,
        user_identifier: str,
        state_key: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get an agent's state.

        Args:
            agent_id: The agent ID.
            user_identifier: The user identifier.
            state_key: The state key.

        Returns:
            The agent state data, or None if not found.
        """
        async with SessionLocal() as session:
            result = await session.execute(
                select(AgentState).where(
                    AgentState.agent_id == agent_id,
                    AgentState.user_identifier == user_identifier,
                    AgentState.state_key == state_key
                )
            )
            agent_state = result.scalars().first()

            if agent_state:
                return agent_state.state_data
            return None

    @staticmethod
    async def update_agent_state(
        agent_id: str,
        user_identifier: str,
        state_key: str,
        state_data: Dict[str, Any]
    ) -> AgentState:
        """
        Update an agent's state.

        Args:
            agent_id: The agent ID.
            user_identifier: The user identifier.
            state_key: The state key.
            state_data: The state data.

        Returns:
            The updated agent state.
        """
        async with SessionLocal() as session:
            # Check if the state already exists
            result = await session.execute(
                select(AgentState).where(
                    AgentState.agent_id == agent_id,
                    AgentState.user_identifier == user_identifier,
                    AgentState.state_key == state_key
                )
            )
            agent_state = result.scalars().first()

            if agent_state:
                # Update existing state
                agent_state.state_data = state_data
                agent_state.last_updated = datetime.now()
            else:
                # Create new state
                agent_state = AgentState(
                    agent_id=agent_id,
                    user_identifier=user_identifier,
                    state_key=state_key,
                    state_data=state_data
                )
                session.add(agent_state)

            await session.commit()
            await session.refresh(agent_state)
            return agent_state

    @staticmethod
    async def delete_agent_state(
        agent_id: str,
        user_identifier: str,
        state_key: str
    ) -> bool:
        """
        Delete an agent's state.

        Args:
            agent_id: The agent ID.
            user_identifier: The user identifier.
            state_key: The state key.

        Returns:
            True if the state was deleted, False otherwise.
        """
        async with SessionLocal() as session:
            result = await session.execute(
                delete(AgentState).where(
                    AgentState.agent_id == agent_id,
                    AgentState.user_identifier == user_identifier,
                    AgentState.state_key == state_key
                )
            )
            await session.commit()
            return result.rowcount > 0

    # --- Agent Task Methods ---

    @staticmethod
    async def create_agent_task(
        task_id: str,
        agent_id: str,
        user_identifier: str,
        task_type: str,
        input_data: Optional[Dict[str, Any]] = None
    ) -> AgentTask:
        """
        Create a new agent task.

        Args:
            task_id: The task ID.
            agent_id: The agent ID.
            user_identifier: The user identifier.
            task_type: The type of task.
            input_data: The input data for the task.

        Returns:
            The created agent task.
        """
        async with SessionLocal() as session:
            task = AgentTask(
                id=task_id,
                agent_id=agent_id,
                user_identifier=user_identifier,
                task_type=task_type,
                status="CREATED",
                input_data=input_data
            )
            session.add(task)
            await session.commit()
            await session.refresh(task)
            return task

    @staticmethod
    async def update_agent_task(
        task_id: str,
        status: Optional[str] = None,
        result_data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        started: bool = False,
        completed: bool = False
    ) -> Optional[AgentTask]:
        """
        Update an agent task.

        Args:
            task_id: The task ID.
            status: The new status of the task.
            result_data: The result data of the task.
            error: Any error message.
            started: Whether the task has started.
            completed: Whether the task is completed.

        Returns:
            The updated agent task, or None if not found.
        """
        async with SessionLocal() as session:
            # Get the task
            result = await session.execute(
                select(AgentTask).where(AgentTask.id == task_id)
            )
            task = result.scalars().first()

            if not task:
                logger.warning(f"Agent task {task_id} not found for update")
                return None

            # Update the task
            if status:
                task.status = status

            if result_data:
                task.result_data = result_data

            if error:
                task.error = error

            if started and not task.started_at:
                task.started_at = datetime.now()

            if completed:
                task.completed_at = datetime.now()

            await session.commit()
            await session.refresh(task)
            return task

    @staticmethod
    async def get_agent_task(task_id: str) -> Optional[AgentTask]:
        """
        Get an agent task by ID.

        Args:
            task_id: The task ID.

        Returns:
            The agent task, or None if not found.
        """
        async with SessionLocal() as session:
            result = await session.execute(
                select(AgentTask).where(AgentTask.id == task_id)
            )
            return result.scalars().first()

    @staticmethod
    async def get_agent_tasks_by_user(
        agent_id: str,
        user_identifier: str,
        status: Optional[str] = None,
        limit: int = 10
    ) -> List[AgentTask]:
        """
        Get agent tasks by user.

        Args:
            agent_id: The agent ID.
            user_identifier: The user identifier.
            status: Optional status filter.
            limit: Maximum number of tasks to return.

        Returns:
            A list of agent tasks.
        """
        async with SessionLocal() as session:
            query = select(AgentTask).where(
                AgentTask.agent_id == agent_id,
                AgentTask.user_identifier == user_identifier
            )

            if status:
                query = query.where(AgentTask.status == status)

            query = query.order_by(AgentTask.created_at.desc()).limit(limit)

            result = await session.execute(query)
            return result.scalars().all()
