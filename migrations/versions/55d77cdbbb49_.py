"""empty message

Revision ID: 55d77cdbbb49
Revises: d210860eb46a
Create Date: 2022-12-06 10:09:50.254449

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '55d77cdbbb49'
down_revision = 'd210860eb46a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('shirt_size', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('accomodations', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('accomodations')
        batch_op.drop_column('shirt_size')

    # ### end Alembic commands ###
