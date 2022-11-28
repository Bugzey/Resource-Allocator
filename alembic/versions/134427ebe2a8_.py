"""empty message

Revision ID: 134427ebe2a8
Revises: 38e9aa8b0389
Create Date: 2022-11-24 18:02:21.134127

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '134427ebe2a8'
down_revision = '38e9aa8b0389'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('is_external', sa.Boolean(), server_default='false', nullable=False), schema='resource_allocator')
    op.alter_column('user', 'password_hash',
               existing_type=sa.VARCHAR(length=255),
               nullable=True,
               schema='resource_allocator')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'password_hash',
               existing_type=sa.VARCHAR(length=255),
               nullable=False,
               schema='resource_allocator')
    op.drop_column('user', 'is_external', schema='resource_allocator')
    # ### end Alembic commands ###
