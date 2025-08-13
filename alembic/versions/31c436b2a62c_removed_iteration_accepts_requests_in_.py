"""Removed iteration.accepts_requests in favour of iteration.is_allocated

Revision ID: 31c436b2a62c
Revises: 2c0ac3d2c214
Create Date: 2025-08-13 17:31:25.549915

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '31c436b2a62c'
down_revision = '2c0ac3d2c214'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'iteration',
        sa.Column('is_allocated', sa.Boolean(), server_default='false', nullable=False),
        schema='resource_allocator',
    )
    op.drop_column('iteration', 'accepts_requests', schema='resource_allocator')
    op.alter_column(
        'request', 'request_status_id',
        existing_type=sa.INTEGER(),
        nullable=False,
        schema='resource_allocator',
    )
    con = op.get_bind()
    con.execute(sa.text("update resource_allocator.iteration set is_allocated = true"))


def downgrade() -> None:
    op.alter_column(
        'request', 'request_status_id',
        existing_type=sa.INTEGER(),
        nullable=True,
        schema='resource_allocator',
    )
    op.add_column(
        'iteration',
        sa.Column(
            'accepts_requests',
            sa.BOOLEAN(),
            server_default=sa.text('true'),
            autoincrement=False,
            nullable=False,
        ),
        schema='resource_allocator',
    )
    op.drop_column('iteration', 'is_allocated', schema='resource_allocator')
    con = op.get_bind()
    con.execute(sa.text("update resource_allocator.iteration set accepts_requests = false"))
