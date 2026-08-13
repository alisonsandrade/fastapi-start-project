"""add rbac (roles, permissions) and user.role_id

Revision ID: 8a44bf3f1560
Revises: 8d6f7210ef75
Create Date: 2026-08-11 21:42:19.019500

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '8a44bf3f1560'
down_revision: Union[str, Sequence[str], None] = '8d6f7210ef75'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'permissions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('code', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_permissions_code'), 'permissions', ['code'], unique=True)

    op.create_table(
        'roles',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('is_system', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_roles_name'), 'roles', ['name'], unique=True)

    op.create_table(
        'role_permissions',
        sa.Column('role_id', sa.String(length=36), nullable=False),
        sa.Column('permission_id', sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('role_id', 'permission_id'),
    )

    with op.batch_alter_table('users') as batch:
        batch.add_column(sa.Column('role_id', sa.String(length=36), nullable=False))
        batch.drop_column('role')
        batch.create_foreign_key(
            'fk_users_role_id_roles',
            'roles',
            ['role_id'],
            ['id'],
            ondelete='RESTRICT',
        )
    op.create_index(op.f('ix_users_role_id'), 'users', ['role_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_users_role_id'), table_name='users')

    with op.batch_alter_table('users') as batch:
        batch.drop_constraint('fk_users_role_id_roles', type_='foreignkey')
        batch.add_column(sa.Column('role', sa.String(length=20), nullable=False))
        batch.drop_column('role_id')

    op.drop_table('role_permissions')
    op.drop_index(op.f('ix_roles_name'), table_name='roles')
    op.drop_table('roles')
    op.drop_index(op.f('ix_permissions_code'), table_name='permissions')
    op.drop_table('permissions')
