"""create divisions table

Revision ID: 3a7c5a68d4f5
Revises: 2d9c31744e38
Create Date: 2023-06-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3a7c5a68d4f5'
down_revision = '2d9c31744e38'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'divisions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['parent_id'], ['divisions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_divisions_code'), 'divisions', ['code'], unique=False)
    op.create_index(op.f('ix_divisions_id'), 'divisions', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_divisions_id'), table_name='divisions')
    op.drop_index(op.f('ix_divisions_code'), table_name='divisions')
    op.drop_table('divisions') 