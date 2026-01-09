"""create_analyses_and_competitors_tables

Revision ID: 64b8de4ca322
Revises: 18c7abce0848
Create Date: 2026-01-08 09:45:26.270541

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '64b8de4ca322'
down_revision: Union[str, Sequence[str], None] = '18c7abce0848'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create enum type for analysis status
    op.execute("""
        CREATE TYPE analysis_status AS ENUM (
            'draft', 'ready', 'querying', 'completed', 'failed'
        )
    """)

    # Create analyses table
    op.create_table(
        'analyses',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('brand_name', sa.String(255), nullable=False),
        sa.Column('status', sa.Enum(
            'draft', 'ready', 'querying', 'completed', 'failed',
            name='analysis_status'
        ), nullable=False, server_default='draft'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Create indexes for analyses
    op.create_index('ix_analyses_id', 'analyses', ['id'])
    op.create_index('ix_analyses_user_id', 'analyses', ['user_id'])
    op.create_index('ix_analyses_brand_name', 'analyses', ['brand_name'])
    op.create_index('ix_analyses_status', 'analyses', ['status'])

    # Create competitors table
    op.create_table(
        'competitors',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('analysis_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('is_suggested', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['analysis_id'], ['analyses.id'], ondelete='CASCADE'),
    )

    # Create indexes for competitors
    op.create_index('ix_competitors_id', 'competitors', ['id'])
    op.create_index('ix_competitors_analysis_id', 'competitors', ['analysis_id'])
    op.create_index('ix_competitors_name', 'competitors', ['name'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes for competitors
    op.drop_index('ix_competitors_name', 'competitors')
    op.drop_index('ix_competitors_analysis_id', 'competitors')
    op.drop_index('ix_competitors_id', 'competitors')

    # Drop competitors table
    op.drop_table('competitors')

    # Drop indexes for analyses
    op.drop_index('ix_analyses_status', 'analyses')
    op.drop_index('ix_analyses_brand_name', 'analyses')
    op.drop_index('ix_analyses_user_id', 'analyses')
    op.drop_index('ix_analyses_id', 'analyses')

    # Drop analyses table
    op.drop_table('analyses')

    # Drop enum type
    op.execute('DROP TYPE analysis_status')
