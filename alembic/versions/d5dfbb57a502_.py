"""empty message

Revision ID: d5dfbb57a502
Revises: 134427ebe2a8
Create Date: 2023-07-26 18:25:18.902476

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd5dfbb57a502'
down_revision = '134427ebe2a8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('image_properties',
    sa.Column('id', sa.Float(), nullable=False),
    sa.Column('created_time', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_time', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('box_x', sa.Float(), nullable=True),
    sa.Column('box_y', sa.Float(), nullable=True),
    sa.Column('box_width', sa.Float(), nullable=True),
    sa.Column('box_height', sa.Float(), nullable=True),
    sa.Column('box_rotation', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    schema='resource_allocator'
    )
    op.create_table('image_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_time', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_time', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('image_type', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('image_type'),
    schema='resource_allocator'
    )
    op.create_table('image',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_time', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_time', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('image_data', sa.LargeBinary(), nullable=False),
    sa.Column('image_type_id', sa.Integer(), nullable=False),
    sa.Column('size_bytes', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['image_type_id'], ['resource_allocator.image_type.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='resource_allocator'
    )
    op.add_column('resource', sa.Column('image_id', sa.Integer(), nullable=True), schema='resource_allocator')
    op.add_column('resource', sa.Column('image_properties_id', sa.Integer(), nullable=True), schema='resource_allocator')
    op.create_foreign_key(None, 'resource', 'image', ['image_id'], ['id'], source_schema='resource_allocator', referent_schema='resource_allocator')
    op.create_foreign_key(None, 'resource', 'image_properties', ['image_properties_id'], ['id'], source_schema='resource_allocator', referent_schema='resource_allocator')
    op.add_column('resource_group', sa.Column('image_id', sa.Integer(), nullable=True), schema='resource_allocator')
    op.add_column('resource_group', sa.Column('image_properties_id', sa.Integer(), nullable=True), schema='resource_allocator')
    op.create_foreign_key(None, 'resource_group', 'image', ['image_id'], ['id'], source_schema='resource_allocator', referent_schema='resource_allocator')
    op.create_foreign_key(None, 'resource_group', 'image_properties', ['image_properties_id'], ['id'], source_schema='resource_allocator', referent_schema='resource_allocator')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'resource_group', schema='resource_allocator', type_='foreignkey')
    op.drop_constraint(None, 'resource_group', schema='resource_allocator', type_='foreignkey')
    op.drop_column('resource_group', 'image_properties_id', schema='resource_allocator')
    op.drop_column('resource_group', 'image_id', schema='resource_allocator')
    op.drop_constraint(None, 'resource', schema='resource_allocator', type_='foreignkey')
    op.drop_constraint(None, 'resource', schema='resource_allocator', type_='foreignkey')
    op.drop_column('resource', 'image_properties_id', schema='resource_allocator')
    op.drop_column('resource', 'image_id', schema='resource_allocator')
    op.drop_table('image', schema='resource_allocator')
    op.drop_table('image_type', schema='resource_allocator')
    op.drop_table('image_properties', schema='resource_allocator')
    # ### end Alembic commands ###
