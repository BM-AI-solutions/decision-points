"""Add workflow and agent state tables

Revision ID: 20240701_001
Revises: 
Create Date: 2024-07-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20240701_001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create workflows table
    op.create_table(
        'workflows',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('initial_topic', sa.String(), nullable=False),
        sa.Column('target_url', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('current_step', sa.String(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('market_research_result', sa.JSON(), nullable=True),
        sa.Column('product_spec_data', sa.JSON(), nullable=True),
        sa.Column('brand_package_data', sa.JSON(), nullable=True),
        sa.Column('code_generation_result', sa.JSON(), nullable=True),
        sa.Column('deployment_result', sa.JSON(), nullable=True),
        sa.Column('marketing_result', sa.JSON(), nullable=True),
        sa.Column('final_result', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workflows_id'), 'workflows', ['id'], unique=False)
    
    # Create workflow_steps table
    op.create_table(
        'workflow_steps',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('workflow_id', sa.String(), nullable=False),
        sa.Column('step_name', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('result', sa.JSON(), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflows.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workflow_steps_id'), 'workflow_steps', ['id'], unique=False)
    
    # Create agent_states table
    op.create_table(
        'agent_states',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('agent_id', sa.String(), nullable=False),
        sa.Column('user_identifier', sa.String(), nullable=False),
        sa.Column('state_key', sa.String(), nullable=False),
        sa.Column('state_data', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('agent_id', 'user_identifier', 'state_key')
    )
    op.create_index(op.f('ix_agent_states_agent_id'), 'agent_states', ['agent_id'], unique=False)
    op.create_index(op.f('ix_agent_states_id'), 'agent_states', ['id'], unique=False)
    op.create_index(op.f('ix_agent_states_user_identifier'), 'agent_states', ['user_identifier'], unique=False)
    
    # Create agent_tasks table
    op.create_table(
        'agent_tasks',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('agent_id', sa.String(), nullable=False),
        sa.Column('user_identifier', sa.String(), nullable=False),
        sa.Column('task_type', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('input_data', sa.JSON(), nullable=True),
        sa.Column('result_data', sa.JSON(), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_tasks_agent_id'), 'agent_tasks', ['agent_id'], unique=False)
    op.create_index(op.f('ix_agent_tasks_id'), 'agent_tasks', ['id'], unique=False)
    op.create_index(op.f('ix_agent_tasks_user_identifier'), 'agent_tasks', ['user_identifier'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_agent_tasks_user_identifier'), table_name='agent_tasks')
    op.drop_index(op.f('ix_agent_tasks_id'), table_name='agent_tasks')
    op.drop_index(op.f('ix_agent_tasks_agent_id'), table_name='agent_tasks')
    op.drop_table('agent_tasks')
    
    op.drop_index(op.f('ix_agent_states_user_identifier'), table_name='agent_states')
    op.drop_index(op.f('ix_agent_states_id'), table_name='agent_states')
    op.drop_index(op.f('ix_agent_states_agent_id'), table_name='agent_states')
    op.drop_table('agent_states')
    
    op.drop_index(op.f('ix_workflow_steps_id'), table_name='workflow_steps')
    op.drop_table('workflow_steps')
    
    op.drop_index(op.f('ix_workflows_id'), table_name='workflows')
    op.drop_table('workflows')
