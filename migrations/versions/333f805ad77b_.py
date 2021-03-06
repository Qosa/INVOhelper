"""empty message

Revision ID: 333f805ad77b
Revises: 4c3938f92bb4
Create Date: 2021-01-09 13:23:55.878710

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '333f805ad77b'
down_revision = '4c3938f92bb4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('evidenced', 'inv_number')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('evidenced', sa.Column('inv_number', sa.VARCHAR(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
