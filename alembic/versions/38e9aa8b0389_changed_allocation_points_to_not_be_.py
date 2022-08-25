"""Changed allocation.points to not be mandatory

Revision ID: 38e9aa8b0389
Revises: 9fb8acb8ff83
Create Date: 2022-08-25 19:16:15.651498

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '38e9aa8b0389'
down_revision = '9fb8acb8ff83'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('allocation', 'points',
               existing_type=sa.INTEGER(),
               nullable=True,
               schema='resource_allocator')
    op.drop_column('allocation', 'total_points', schema='resource_allocator')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('allocation', sa.Column('total_points', sa.INTEGER(), autoincrement=False, nullable=False), schema='resource_allocator')
    op.alter_column('allocation', 'points',
               existing_type=sa.INTEGER(),
               nullable=False,
               schema='resource_allocator')
    # ### end Alembic commands ###
