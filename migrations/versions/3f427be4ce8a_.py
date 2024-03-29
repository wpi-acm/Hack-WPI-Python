"""empty message

Revision ID: 3f427be4ce8a
Revises: 55d77cdbbb49
Create Date: 2022-12-06 10:18:07.322064

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3f427be4ce8a'
down_revision = '55d77cdbbb49'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('checked_in', sa.Boolean(),
                                      nullable=False, default=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('checked_in')

    # ### end Alembic commands ###
