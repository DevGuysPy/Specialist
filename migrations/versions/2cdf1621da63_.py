"""empty message

Revision ID: 2cdf1621da63
Revises: 68c7c71f40c9
Create Date: 2016-01-23 21:01:24.272882

"""

# revision identifiers, used by Alembic.
revision = '2cdf1621da63'
down_revision = '68c7c71f40c9'

from alembic import op
import sqlalchemy as sa

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('birth_date', sa.Date(), nullable=False))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'birth_date')
    ### end Alembic commands ###
