"""empty message

Revision ID: f500960aeb42
Revises: 58dd1d23dea4
Create Date: 2020-11-12 21:48:21.473647

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f500960aeb42'
down_revision = '58dd1d23dea4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('stocktaking', sa.Column('date_start', sa.DateTime(), nullable=True))
    op.add_column('stocktaking', sa.Column('date_stop', sa.DateTime(), nullable=True))
    op.add_column('unknown', sa.Column('inv_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'unknown', 'stocktaking', ['inv_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'unknown', type_='foreignkey')
    op.drop_column('unknown', 'inv_id')
    op.drop_column('stocktaking', 'date_stop')
    op.drop_column('stocktaking', 'date_start')
    # ### end Alembic commands ###
