"""Added allocation.user_for_id

Revision ID: a8144ecbef28
Revises: 31c436b2a62c
Create Date: 2026-08-20 17:09:44.498124

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a8144ecbef28'
down_revision = '31c436b2a62c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'allocation',
        sa.Column('user_for_id', sa.Integer(), nullable=True),
        schema='resource_allocator',
    )

    #   Pre-fill user_for_id = user_id
    allocation = sa.Table(
        "allocation",
        sa.MetaData(),
        autoload_with=op.get_bind(),
        schema="resource_allocator",
    )
    op.execute(
        sa.update(allocation)
        .values(user_for_id=allocation.c["user_id"])
    )
    op.alter_column("allocation", "user_for_id", nullable=False, schema="resource_allocator")

    #   Foreign Key
    op.create_foreign_key(
        "allocation_user_for_id_fkey",
        'allocation',
        'user',
        ['user_for_id'],
        ['id'],
        source_schema='resource_allocator',
        referent_schema='resource_allocator',
    )


def downgrade() -> None:
    op.drop_constraint(
        "allocation_user_for_id_fkey",
        'allocation',
        schema='resource_allocator',
        type_='foreignkey',
    )
    op.drop_column('allocation', 'user_for_id', schema='resource_allocator')
