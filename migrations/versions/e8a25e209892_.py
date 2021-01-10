"""empty message

Revision ID: e8a25e209892
Revises: c4f8b2d91290
Create Date: 2021-01-08 22:00:07.223743

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e8a25e209892'
down_revision = 'c4f8b2d91290'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('evidenced', sa.Column('deleted', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('evidenced', 'deleted')
    # ### end Alembic commands ###
