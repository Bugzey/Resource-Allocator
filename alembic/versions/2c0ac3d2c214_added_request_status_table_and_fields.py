"""Added request status table and fields

Revision ID: 2c0ac3d2c214
Revises: 9627bdb6499f
Create Date: 2025-05-07 13:54:02.237107

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2c0ac3d2c214'
down_revision = '9627bdb6499f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'request_status',
        sa.Column('request_status', sa.String(), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_time', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_time', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='resource_allocator'
    )
    status_table = sa.Table(
        "request_status", sa.MetaData(), schema="resource_allocator", autoload_with=op.get_bind(),
    )
    op.bulk_insert(
        status_table,
        [
            {"request_status": "New"},
            {"request_status": "Completed"},
            {"request_status": "Declined"},
        ],
    )

    con = op.get_bind()
    query = (
        sa.select(status_table.c["id"])
        .where(status_table.c["request_status"] == "New")
    )
    new_request_id = con.execute(query).scalar()

    op.add_column(
        'request',
        sa.Column('request_status_id', sa.Integer(), nullable=True),
        schema='resource_allocator',
    )

    request = sa.Table(
        "request", sa.MetaData(), schema="resource_allocator", autoload_with=op.get_bind()
    )
    op.execute(
        sa.update(request)
        .where(request.c.request_status_id.is_(None))
        .values({request.c.request_status_id: new_request_id})
    )

    op.alter_column(
        "request",
        "request_status_id",
        nullable=True,
        schema="resource_allocator",
    )
    op.create_foreign_key(
        "request_request_status_id_fkey",
        'request',
        'request_status',
        ['request_status_id'],
        ['id'],
        source_schema='resource_allocator',
        referent_schema='resource_allocator',
    )


def downgrade() -> None:
    op.drop_constraint(
        "request_request_status_id_fkey",
        'request',
        schema='resource_allocator',
        type_='foreignkey',
    )
    op.drop_column('request', 'request_status_id', schema='resource_allocator')
    op.drop_table('request_status', schema='resource_allocator')
