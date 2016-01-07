"""empty message

Revision ID: 2b17f7fc56b9
Revises: 82f9c9780e52
Create Date: 2016-01-07 12:16:47.511585

"""

# revision identifiers, used by Alembic.
revision = '2b17f7fc56b9'
down_revision = '82f9c9780e52'

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('phone_number', sqlalchemy_utils.types.phone_number.PhoneNumberType(length=20), nullable=True))
    op.drop_column('user', 'phone')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('phone', sa.VARCHAR(length=12), autoincrement=False, nullable=True))
    op.drop_column('user', 'phone_number')
    ### end Alembic commands ###
