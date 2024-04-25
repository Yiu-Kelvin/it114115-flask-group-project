"""added accepting answer

Revision ID: 2b71e04b6ffc
Revises: 9f728f8a9dfa
Create Date: 2024-04-24 01:15:38.151012

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2b71e04b6ffc'
down_revision = '9f728f8a9dfa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('answer', schema=None) as batch_op:
        batch_op.add_column(sa.Column('accepted', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('answer', schema=None) as batch_op:
        batch_op.drop_column('accepted')

    # ### end Alembic commands ###