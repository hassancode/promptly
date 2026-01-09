"""create ai_responses and citations tables

Revision ID: e7f9a8b3c2d1
Revises: c96939c4414f
Create Date: 2026-01-08 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e7f9a8b3c2d1'
down_revision: Union[str, None] = 'c96939c4414f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create ENUM types
    op.execute("CREATE TYPE provider_type AS ENUM ('openai', 'gemini', 'claude', 'perplexity', 'google_ai', 'huggingface')")
    op.execute("CREATE TYPE citation_coverage AS ENUM ('none', 'partial', 'complete')")
    op.execute("CREATE TYPE response_status AS ENUM ('pending', 'in_progress', 'success', 'failed', 'timeout')")
    op.execute("CREATE TYPE source_type AS ENUM ('web', 'academic', 'news', 'documentation', 'other')")
    op.execute("CREATE TYPE validity_status AS ENUM ('valid', 'broken', 'unknown')")

    # Create ai_responses table
    op.create_table('ai_responses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('prompt_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('provider', sa.Enum('openai', 'gemini', 'claude', 'perplexity', 'google_ai', 'huggingface', name='provider_type'), nullable=False),
        sa.Column('model_name', sa.String(length=100), nullable=False),
        sa.Column('answer_text', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('citation_coverage', sa.Enum('none', 'partial', 'complete', name='citation_coverage'), nullable=False),
        sa.Column('status', sa.Enum('pending', 'in_progress', 'success', 'failed', 'timeout', name='response_status'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['prompt_id'], ['prompts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_responses_id'), 'ai_responses', ['id'], unique=False)
    op.create_index(op.f('ix_ai_responses_prompt_id'), 'ai_responses', ['prompt_id'], unique=False)
    op.create_index(op.f('ix_ai_responses_provider'), 'ai_responses', ['provider'], unique=False)
    op.create_index(op.f('ix_ai_responses_status'), 'ai_responses', ['status'], unique=False)

    # Create GIN index on answer_text JSONB column for full-text search
    op.execute('CREATE INDEX ix_ai_responses_answer_text_gin ON ai_responses USING GIN (answer_text jsonb_path_ops)')

    # Create citations table
    op.create_table('citations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ai_response_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=True),
        sa.Column('snippet', sa.Text(), nullable=True),
        sa.Column('source_type', sa.Enum('web', 'academic', 'news', 'documentation', 'other', name='source_type'), nullable=False),
        sa.Column('validity_status', sa.Enum('valid', 'broken', 'unknown', name='validity_status'), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['ai_response_id'], ['ai_responses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_citations_id'), 'citations', ['id'], unique=False)
    op.create_index(op.f('ix_citations_ai_response_id'), 'citations', ['ai_response_id'], unique=False)


def downgrade() -> None:
    # Drop indexes and tables
    op.drop_index(op.f('ix_citations_ai_response_id'), table_name='citations')
    op.drop_index(op.f('ix_citations_id'), table_name='citations')
    op.drop_table('citations')

    op.execute('DROP INDEX IF EXISTS ix_ai_responses_answer_text_gin')
    op.drop_index(op.f('ix_ai_responses_status'), table_name='ai_responses')
    op.drop_index(op.f('ix_ai_responses_provider'), table_name='ai_responses')
    op.drop_index(op.f('ix_ai_responses_prompt_id'), table_name='ai_responses')
    op.drop_index(op.f('ix_ai_responses_id'), table_name='ai_responses')
    op.drop_table('ai_responses')

    # Drop ENUM types
    op.execute('DROP TYPE validity_status')
    op.execute('DROP TYPE source_type')
    op.execute('DROP TYPE response_status')
    op.execute('DROP TYPE citation_coverage')
    op.execute('DROP TYPE provider_type')
