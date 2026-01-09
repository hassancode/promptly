"""create_prompts_table

Revision ID: c96939c4414f
Revises: 64b8de4ca322
Create Date: 2026-01-08 10:12:24.302924

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c96939c4414f'
down_revision: Union[str, Sequence[str], None] = '64b8de4ca322'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create prompts table
    op.create_table(
        'prompts',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('analysis_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('is_suggested', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['analysis_id'], ['analyses.id'], ondelete='CASCADE'),
    )

    # Create indexes for prompts
    op.create_index('ix_prompts_id', 'prompts', ['id'])
    op.create_index('ix_prompts_analysis_id', 'prompts', ['analysis_id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes for prompts
    op.drop_index('ix_prompts_analysis_id', 'prompts')
    op.drop_index('ix_prompts_id', 'prompts')

    # Drop prompts table
    op.drop_table('prompts')
