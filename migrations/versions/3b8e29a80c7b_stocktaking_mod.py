"""stocktaking mod

Revision ID: 3b8e29a80c7b
Revises: fc7ed2c5a64a
Create Date: 2020-12-04 13:11:24.025131

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3b8e29a80c7b'
down_revision = 'fc7ed2c5a64a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('evidenced',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('inv_id', sa.Integer(), nullable=True),
    sa.Column('item_id', sa.Integer(), nullable=True),
    sa.Column('add_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['inv_id'], ['stocktaking.id'], ),
    sa.ForeignKeyConstraint(['item_id'], ['items_list.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('nonevidenced',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('inv_id', sa.Integer(), nullable=True),
    sa.Column('item_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['inv_id'], ['stocktaking.id'], ),
    sa.ForeignKeyConstraint(['item_id'], ['items_list.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_column('stocktaking', 'unknown')
    op.drop_column('stocktaking', 'evidenced')
    op.drop_column('stocktaking', 'non_evidenced')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('stocktaking', sa.Column('non_evidenced', postgresql.ARRAY(sa.INTEGER()), autoincrement=False, nullable=True))
    op.add_column('stocktaking', sa.Column('evidenced', postgresql.ARRAY(sa.INTEGER()), autoincrement=False, nullable=True))
    op.add_column('stocktaking', sa.Column('unknown', postgresql.ARRAY(sa.INTEGER()), autoincrement=False, nullable=True))
    op.drop_table('nonevidenced')
    op.drop_table('evidenced')
    # ### end Alembic commands ###
