"""Misc alembic fixes

Revision ID: 9627bdb6499f
Revises: d5dfbb57a502
Create Date: 2025-05-07 11:34:14.761609

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9627bdb6499f'
down_revision = 'd5dfbb57a502'
branch_labels = None
depends_on = None


def upgrade() -> None:
    for table_name, col in [
        ("allocation", "points"),
        ("image_properties", "box_x"),
        ("image_properties", "box_y"),
        ("image_properties", "box_width"),
        ("image_properties", "box_height"),
        ("image_properties", "box_rotation"),
    ]:
        table = sa.Table(
            table_name,
            sa.MetaData(),
            autoload_with=op.get_bind(),
            schema="resource_allocator",
        )
        op.execute(sa.update(table).where(table.c[col].is_(None)).values({col: 0}))

    op.alter_column(
            'allocation', 'points',
            existing_type=sa.INTEGER(),
            nullable=True,
            schema='resource_allocator')
    op.alter_column(
            'image_properties', 'box_x',
            existing_type=sa.DOUBLE_PRECISION(precision=53),
            nullable=False,
            schema='resource_allocator')
    op.alter_column(
            'image_properties', 'box_y',
            existing_type=sa.DOUBLE_PRECISION(precision=53),
            nullable=False,
            schema='resource_allocator')
    op.alter_column(
            'image_properties', 'box_width',
            existing_type=sa.DOUBLE_PRECISION(precision=53),
            nullable=False,
            schema='resource_allocator')
    op.alter_column(
            'image_properties', 'box_height',
            existing_type=sa.DOUBLE_PRECISION(precision=53),
            nullable=False,
            schema='resource_allocator')
    op.alter_column(
            'image_properties', 'box_rotation',
            existing_type=sa.DOUBLE_PRECISION(precision=53),
            nullable=False,
            schema='resource_allocator')
    op.alter_column(
            'resource', 'top_resource_group_id',
            existing_type=sa.INTEGER(),
            nullable=False,
            schema='resource_allocator')


def downgrade() -> None:
    op.alter_column(
            'resource', 'top_resource_group_id',
            existing_type=sa.INTEGER(),
            nullable=True,
            schema='resource_allocator')
    op.alter_column(
            'image_properties', 'box_rotation',
            existing_type=sa.DOUBLE_PRECISION(precision=53),
            nullable=True,
            schema='resource_allocator')
    op.alter_column(
            'image_properties', 'box_height',
            existing_type=sa.DOUBLE_PRECISION(precision=53),
            nullable=True,
            schema='resource_allocator')
    op.alter_column(
            'image_properties', 'box_width',
            existing_type=sa.DOUBLE_PRECISION(precision=53),
            nullable=True,
            schema='resource_allocator')
    op.alter_column(
            'image_properties', 'box_y',
            existing_type=sa.DOUBLE_PRECISION(precision=53),
            nullable=True,
            schema='resource_allocator')
    op.alter_column(
            'image_properties', 'box_x',
            existing_type=sa.DOUBLE_PRECISION(precision=53),
            nullable=True,
            schema='resource_allocator')
    op.alter_column(
            'allocation', 'points',
            existing_type=sa.INTEGER(),
            nullable=True,
            schema='resource_allocator')
