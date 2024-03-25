"""empty message

Revision ID: 20c72b5aa489
Revises: a5307b27195c
Create Date: 2024-03-04 10:51:58.890749

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20c72b5aa489'
down_revision = 'a5307b27195c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('attendance_record', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date', sa.Date(), nullable=False))
        batch_op.drop_column('status')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('attendance_record', schema=None) as batch_op:
        batch_op.add_column(sa.Column('status', sa.VARCHAR(length=6), nullable=False))
        batch_op.drop_column('date')

    # ### end Alembic commands ###
