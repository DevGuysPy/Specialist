"""empty message

Revision ID: fa5e6febc82a
Revises: 2b17f7fc56b9
Create Date: 2016-01-07 12:54:04.581114

"""

# revision identifiers, used by Alembic.
revision = 'fa5e6febc82a'
down_revision = '2b17f7fc56b9'

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
from main.models import UserOrgActivity, get_experience_types


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('location',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('country', sa.String(), nullable=False),
    sa.Column('city', sa.String(), nullable=True),
    sa.Column('street', sa.String(), nullable=True),
    sa.Column('building', sa.String(), nullable=True),
    sa.Column('apartment', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('org_category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('service',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=256), nullable=False),
    sa.Column('domain', sa.String(length=256), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('company',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.Column('website', sqlalchemy_utils.types.url.URLType(), nullable=True),
    sa.Column('logo', sa.String(), nullable=True),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.Column('location_id', sa.Integer(), nullable=True),
    sa.Column('created_time', sa.DateTime(), nullable=True),
    sa.Column('confirmed', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['org_category.id'], ),
    sa.ForeignKeyConstraint(['location_id'], ['location.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('logo'),
    sa.UniqueConstraint('name')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=256), nullable=False),
    sa.Column('first_name', sa.String(length=256), nullable=True),
    sa.Column('last_name', sa.String(length=256), nullable=True),
    sa.Column('password', sqlalchemy_utils.types.password.PasswordType(), nullable=True),
    sa.Column('phone_number', sqlalchemy_utils.types.phone_number.PhoneNumberType(length=20), nullable=True),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('photo', sa.String(), nullable=True),
    sa.Column('location_id', sa.Integer(), nullable=True),
    sa.Column('registration_time', sa.DateTime(), nullable=True),
    sa.Column('confirmed', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['location_id'], ['location.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('photo')
    )
    op.create_table('org_org_activity',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('from_org_id', sa.Integer(), nullable=False),
    sa.Column('to_org_id', sa.Integer(), nullable=False),
    sa.Column('service_id', sa.Integer(), nullable=False),
    sa.Column('start', sa.DateTime(), nullable=True),
    sa.Column('end', sa.DateTime(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('confirmed', sa.Boolean(), nullable=True),
    sa.Column('created_time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['from_org_id'], ['company.id'], ),
    sa.ForeignKeyConstraint(['service_id'], ['service.id'], ),
    sa.ForeignKeyConstraint(['to_org_id'], ['company.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('specialist',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('experience', sqlalchemy_utils.types.choice.ChoiceType(get_experience_types()), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('org_id', sa.Integer(), nullable=True),
    sa.Column('confirmed', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['org_id'], ['company.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_org_activity',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('org_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('service_id', sa.Integer(), nullable=False),
    sa.Column('customer', sqlalchemy_utils.types.choice.ChoiceType(UserOrgActivity.ACTIVITY_TYPE), nullable=True),
    sa.Column('start', sa.DateTime(), nullable=True),
    sa.Column('end', sa.DateTime(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('confirmed', sa.Boolean(), nullable=True),
    sa.Column('created_time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['org_id'], ['company.id'], ),
    sa.ForeignKeyConstraint(['service_id'], ['service.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_user_activity',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('from_user_id', sa.Integer(), nullable=False),
    sa.Column('to_user_id', sa.Integer(), nullable=False),
    sa.Column('service_id', sa.Integer(), nullable=False),
    sa.Column('start', sa.DateTime(), nullable=True),
    sa.Column('end', sa.DateTime(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('specialist_rating', sa.Integer(), nullable=True),
    sa.Column('customer_rating', sa.Integer(), nullable=True),
    sa.Column('confirmed', sa.Boolean(), nullable=True),
    sa.Column('created_time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['from_user_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['service_id'], ['service.id'], ),
    sa.ForeignKeyConstraint(['to_user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('specialist_service',
    sa.Column('specialist_id', sa.Integer(), nullable=False),
    sa.Column('service_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['service_id'], ['service.id'], ),
    sa.ForeignKeyConstraint(['specialist_id'], ['specialist.id'], ),
    sa.PrimaryKeyConstraint('specialist_id', 'service_id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('specialist_service')
    op.drop_table('user_user_activity')
    op.drop_table('user_org_activity')
    op.drop_table('specialist')
    op.drop_table('org_org_activity')
    op.drop_table('user')
    op.drop_table('company')
    op.drop_table('service')
    op.drop_table('org_category')
    op.drop_table('location')
    ### end Alembic commands ###
