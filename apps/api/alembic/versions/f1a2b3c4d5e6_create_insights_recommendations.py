"""Create insights and recommendations tables

Revision ID: f1a2b3c4d5e6
Revises: e7f9a8b3c2d1
Create Date: 2026-01-08

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f1a2b3c4d5e6'
down_revision: Union[str, None] = 'e7f9a8b3c2d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create insight_type enum
    insight_type_enum = postgresql.ENUM(
        'visibility', 'sentiment', 'theme', 'gap', 'comparison', 'mention',
        name='insight_type',
        create_type=True
    )
    insight_type_enum.create(op.get_bind(), checkfirst=True)

    # Create confidence_level enum (for insights)
    confidence_level_enum = postgresql.ENUM(
        'high', 'medium', 'low', 'none',
        name='confidence_level',
        create_type=True
    )
    confidence_level_enum.create(op.get_bind(), checkfirst=True)

    # Create impact_level enum (for recommendations)
    impact_level_enum = postgresql.ENUM(
        'high', 'medium', 'low',
        name='impact_level',
        create_type=True
    )
    impact_level_enum.create(op.get_bind(), checkfirst=True)

    # Create recommendation_confidence_level enum
    rec_confidence_level_enum = postgresql.ENUM(
        'high', 'medium', 'low',
        name='recommendation_confidence_level',
        create_type=True
    )
    rec_confidence_level_enum.create(op.get_bind(), checkfirst=True)

    # Create insights table
    op.create_table(
        'insights',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('analysis_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('analyses.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('insight_type', sa.Enum('visibility', 'sentiment', 'theme', 'gap', 'comparison', 'mention', name='insight_type'), nullable=False),
        sa.Column('brand_name', sa.String(255), nullable=False),
        sa.Column('competitor_name', sa.String(255), nullable=True),
        sa.Column('summary', sa.String(500), nullable=False),
        sa.Column('explanation', sa.Text, nullable=False),
        sa.Column('evidence_references', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('confidence_level', sa.Enum('high', 'medium', 'low', 'none', name='confidence_level'), nullable=False, server_default='medium'),
        sa.Column('scores', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Create GIN index on evidence_references for fast JSONB queries
    op.create_index(
        'ix_insights_evidence_references_gin',
        'insights',
        ['evidence_references'],
        postgresql_using='gin'
    )

    # Create index on insight_type for filtering
    op.create_index('ix_insights_type', 'insights', ['insight_type'])

    # Create recommendations table
    op.create_table(
        'recommendations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('analysis_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('analyses.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('text', sa.Text, nullable=False),
        sa.Column('rationale', sa.Text, nullable=False),
        sa.Column('expected_impact', sa.Enum('high', 'medium', 'low', name='impact_level'), nullable=False, server_default='medium'),
        sa.Column('confidence_level', sa.Enum('high', 'medium', 'low', name='recommendation_confidence_level'), nullable=False, server_default='medium'),
        sa.Column('evidence_references', postgresql.JSONB, nullable=False, server_default='[]'),
        sa.Column('priority', sa.Integer, nullable=False, server_default='5'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Create GIN index on evidence_references for fast JSONB queries
    op.create_index(
        'ix_recommendations_evidence_references_gin',
        'recommendations',
        ['evidence_references'],
        postgresql_using='gin'
    )

    # Create index on priority for ordering
    op.create_index('ix_recommendations_priority', 'recommendations', ['priority'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_recommendations_priority')
    op.drop_index('ix_recommendations_evidence_references_gin')
    op.drop_index('ix_insights_type')
    op.drop_index('ix_insights_evidence_references_gin')

    # Drop tables
    op.drop_table('recommendations')
    op.drop_table('insights')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS recommendation_confidence_level')
    op.execute('DROP TYPE IF EXISTS impact_level')
    op.execute('DROP TYPE IF EXISTS confidence_level')
    op.execute('DROP TYPE IF EXISTS insight_type')
