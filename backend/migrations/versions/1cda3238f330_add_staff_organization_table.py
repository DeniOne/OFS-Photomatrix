"""add staff organization table

Revision ID: 1cda3238f330
Revises: 3870e39b3d8b
Create Date: 2025-04-26 18:48:55.824781

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1cda3238f330'
down_revision: Union[str, None] = '3870e39b3d8b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('function_code_key', 'function', type_='unique')
    op.create_index(op.f('ix_function_code'), 'function', ['code'], unique=True)
    op.create_index(op.f('ix_function_section_id'), 'function', ['section_id'], unique=False)
    op.add_column('staff', sa.Column('organization_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'staff', 'organization', ['organization_id'], ['id'])
    op.drop_index('ix_staff_organization_organization_id', table_name='staff_organization')
    op.drop_index('ix_staff_organization_staff_id', table_name='staff_organization')
    op.drop_constraint('uix_staff_organization', 'staff_organization', type_='unique')
    op.drop_constraint('staff_organization_staff_id_fkey', 'staff_organization', type_='foreignkey')
    op.drop_constraint('staff_organization_organization_id_fkey', 'staff_organization', type_='foreignkey')
    op.create_foreign_key(None, 'staff_organization', 'staff', ['staff_id'], ['id'])
    op.create_foreign_key(None, 'staff_organization', 'organization', ['organization_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'staff_organization', type_='foreignkey')
    op.drop_constraint(None, 'staff_organization', type_='foreignkey')
    op.create_foreign_key('staff_organization_organization_id_fkey', 'staff_organization', 'organization', ['organization_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('staff_organization_staff_id_fkey', 'staff_organization', 'staff', ['staff_id'], ['id'], ondelete='CASCADE')
    op.create_unique_constraint('uix_staff_organization', 'staff_organization', ['staff_id', 'organization_id'])
    op.create_index('ix_staff_organization_staff_id', 'staff_organization', ['staff_id'], unique=False)
    op.create_index('ix_staff_organization_organization_id', 'staff_organization', ['organization_id'], unique=False)
    op.drop_constraint(None, 'staff', type_='foreignkey')
    op.drop_column('staff', 'organization_id')
    op.drop_index(op.f('ix_function_section_id'), table_name='function')
    op.drop_index(op.f('ix_function_code'), table_name='function')
    op.create_unique_constraint('function_code_key', 'function', ['code'])
    # ### end Alembic commands ### 