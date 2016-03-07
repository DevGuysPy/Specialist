import datetime

from flask.ext.login import current_user

from app import db
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy_utils import URLType, ChoiceType, PasswordType,\
    PhoneNumberType, CurrencyType

ACTIVITY_STATUS_TYPES = (
    ('0', 'Waiting for start'),
    ('1', 'In work'),
    ('2', 'Canceled'),
    ('3', 'Failed'),
    ('4', 'Done'),
    ('5', 'Expired')
)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)

    first_name = db.Column(db.String(256))

    last_name = db.Column(db.String(256))

    password = db.Column(PasswordType(
        schemes=[
            'pbkdf2_sha512',
            'md5_crypt'
        ],

        deprecated=['md5_crypt']
    ), nullable=False)

    phone_number = db.Column(PhoneNumberType())

    email = db.Column(db.String(), nullable=False, unique=True)

    profile_photo = db.Column(db.String(), unique=True)

    bg_photo = db.Column(db.String(), nullable=False)

    birth_date = db.Column(db.Date())

    location_id = db.Column(db.Integer, db.ForeignKey('location.id'),
                            nullable=True)
    location = db.relationship('Location')

    specialist = db.relationship("Specialist",
                                 uselist=False)

    registration_time = db.Column(db.DateTime(),
                                  default=datetime.datetime.utcnow)

    confirmed = db.Column(db.Boolean(), default=False)

    def full_name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def get_age(self):
        if not self.birth_date:
            return
        return datetime.date.today().year - self.birth_date.year

    def get_orders(self):
        orders = Activity.query\
            .filter(
                Activity.to_user_id == self.id).all()
        return orders

    def get_active_orders(self):
        active_orders = Activity.query\
            .filter(
                Activity.to_user_id == self.id,
                Activity.start >= datetime.date.today())\
            .order_by(Activity.start.desc()).all()
        return active_orders

    def get_past_orders(self):
        past_offers = Activity.query\
            .filter(
                Activity.to_user_id == self.id,
                Activity.start < datetime.date.today())\
            .order_by(Activity.start.desc()).all()

        return past_offers

    def get_active_offers(self):
        active_orders = Activity.query\
            .filter(
                Activity.from_user_id == self.id,
                Activity.start >= datetime.date.today())\
            .order_by(Activity.start.desc()).all()
        return active_orders

    def get_past_offers(self):
        past_offers = Activity.query\
            .filter(
                Activity.from_user_id == self.id,
                Activity.start < datetime.date.today())\
            .order_by(Activity.start.desc()).all()

        return past_offers

    def __repr__(self):
        return '<User %r>' % (self.full_name())


class SpecialistService(db.Model):
    __tablename__ = 'specialist_service'
    specialist_id = db.Column(db.Integer(), db.ForeignKey('specialist.id'),
                              primary_key=True)
    service_id = db.Column(db.Integer(), db.ForeignKey('service.id'),
                           primary_key=True)


class Company(db.Model):
    __tablename__ = 'company'
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(256), nullable=False, unique=True)

    website = db.Column(URLType)

    logo = db.Column(db.String(), unique=True)

    description = db.Column(db.Text())

    category_id = db.Column(db.Integer(), db.ForeignKey('org_category.id'),
                            nullable=True)
    category = db.relationship('OrgCategory')

    location_id = db.Column(db.Integer, db.ForeignKey('location.id'),
                            nullable=True)
    location = db.relationship('Location')

    created_time = db.Column(db.DateTime(),
                             default=datetime.datetime.utcnow)

    confirmed = db.Column(db.Boolean(), default=False)


def get_experience_types():
    types = [('0', 'Less than 1 year')]
    types.extend(('{}'.format(i), '{} years'.format(i)) for i in range(1, 11))
    types.append(('11', '10+ years'))
    return types


class Specialist(db.Model):
    __tablename__ = 'specialist'
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship("User")

    experience = db.Column(ChoiceType(get_experience_types()), default='0')

    description = db.Column(db.Text())

    services = db.relationship('Service',
                               secondary="specialist_service",
                               backref=db.backref("specialists", lazy='dynamic'))

    org_id = db.Column(db.Integer, db.ForeignKey('company.id'),
                       nullable=True)
    org = db.relationship('Company')

    confirmed = db.Column(db.Boolean(), default=False)

    @hybrid_property
    def location(self):
        return self.user.location.get_name()


class Service(db.Model):
    id = db.Column(db.Integer(), primary_key=True)

    title = db.Column(db.String(256), nullable=False, unique=True)

    category_id = db.Column(db.Integer, db.ForeignKey('service_category.id'),
                            nullable=False)
    category = db.relationship('ServiceCategory',
                               backref=db.backref("services", lazy='dynamic'))

    description = db.Column(db.Text())

    # temporary, for specialist page
    def activities_count(self):
        return Activity.query.filter_by(
            service_id=self.id,
            from_user_id=current_user.id).count()


class ServiceCategory(db.Model):
    id = db.Column(db.Integer(), primary_key=True)

    title = db.Column(db.String(256), nullable=False, unique=True)

    description = db.Column(db.Text())


TIMING_TYPE = (
        ('0', 'Without strict time limits'),
        ('1', 'Moderate'),
        ('2', 'Urgent')
    )


RATING = (
    ('5', 'Excellent'),
    ('4', 'Good'),
    ('3', 'Not bad'),
    ('2', 'Not good'),
    ('1', 'Bad'),
    ('0', 'Not specified')
)

PAYMENT_TYPE = (
    ('0', 'By cash'),
    ('1', 'PayPal'),
    ('2', 'Credit card')
)


class ActivityMember(db.Model):
    __tablename__ = 'activity_member'

    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'),
                        primary_key=True)
    activity_id = db.Column(db.Integer(), db.ForeignKey('activity.id'),
                            primary_key=True)


class Activity(db.Model):
    __tablename__ = 'activity'

    id = db.Column(db.Integer(), primary_key=True)

    from_user_id = db.Column(db.Integer(), db.ForeignKey('users.id'),
                             nullable=False)
    from_user = db.relationship('User', foreign_keys=[from_user_id],
                                backref=db.backref("from_activities_user",
                                                   lazy='dynamic'))

    to_user_id = db.Column(db.Integer(), db.ForeignKey('users.id'),
                           nullable=False)
    to_user = db.relationship('User', foreign_keys=[to_user_id],
                              backref=db.backref("to_activities_user",
                                                 lazy='dynamic'))

    service_id = db.Column(db.Integer(), db.ForeignKey('service.id'),
                           nullable=False)
    service = db.relationship('Service', backref="user_user_activities")

    location_id = db.Column(db.Integer, db.ForeignKey('location.id'),
                            nullable=True)
    location = db.relationship('Location')

    member = db.relationship('User',
                             secondary="activity_member",
                             backref=db.backref("activity", lazy='dynamic'))

    start = db.Column(db.DateTime())
    end = db.Column(db.DateTime())

    title = db.Column(db.Text(), nullable=False)
    description = db.Column(db.Text(), nullable=False)

    price = db.Column(db.Integer(), nullable=True)

    specialist_rating = db.Column(ChoiceType(RATING), default='0')
    customer_rating = db.Column(ChoiceType(RATING), default='0')

    timing_type = db.Column(ChoiceType(TIMING_TYPE), default='0')

    payment_type = db.Column(ChoiceType(PAYMENT_TYPE), default='0')

    status = db.Column(ChoiceType(ACTIVITY_STATUS_TYPES))

    confirmed = db.Column(db.Boolean(), default=False)

    created_time = db.Column(db.DateTime(), default=datetime.datetime.utcnow)

    @classmethod
    def get_or_create(cls,
                      from_user,
                      to_user,
                      service,
                      start,
                      defaults=None):
        """
        Func for adding Activity

        :param User from_user: specialist
        :param User to_user: customer
        :param Service service: service
        :param int start: start
        :param dict defaults: defaults
        :return :
        """

        try:
            activity = Activity.query.filter_by(
                from_user=from_user, to_user=to_user,
                service=service, start=start).one()
            return activity, False
        except NoResultFound:
            activity = Activity(
                from_user=from_user, to_user=to_user,
                service=service, start=start)
            db.session.add(activity)

            if defaults:
                for field, value in defaults.items():
                    if hasattr(cls, field):
                        setattr(activity, field, value)
                    else:
                        raise AttributeError(
                            "ServiceActivity has no attribute {}".format(field))

        return activity, True


ACTIVITY_TYPE = (
        (0, 'User Org'),
        (1, 'Org User')
    )


class UserOrgActivity(db.Model):
    id = db.Column(db.Integer(), primary_key=True)

    org_id = db.Column(db.Integer(), db.ForeignKey('company.id'),
                       nullable=False)
    org = db.relationship('Company', foreign_keys=[org_id],
                          backref="from_activities_user_org")

    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'),
                        nullable=False)
    user = db.relationship('User', foreign_keys=[user_id],
                           backref="to_activities_user_org")

    service_id = db.Column(db.Integer(), db.ForeignKey('service.id'),
                           nullable=False)
    service = db.relationship('Service')

    customer = db.Column(ChoiceType(ACTIVITY_TYPE), default=0)

    start = db.Column(db.DateTime())
    end = db.Column(db.DateTime())
    description = db.Column(db.Text())

    status = db.Column(ChoiceType(ACTIVITY_STATUS_TYPES))

    confirmed = db.Column(db.Boolean(), default=False)

    created_time = db.Column(db.DateTime(), default=datetime.datetime.utcnow)


class OrgOrgActivity(db.Model):
    id = db.Column(db.Integer(), primary_key=True)

    from_org_id = db.Column(db.Integer(), db.ForeignKey('company.id'),
                            nullable=False)
    from_org = db.relationship('Company', foreign_keys=[from_org_id],
                               backref="from_activities_org")

    to_org_id = db.Column(db.Integer(), db.ForeignKey('company.id'),
                          nullable=False)
    to_org = db.relationship('Company', foreign_keys=[to_org_id],
                             backref="to_activities_org")

    service_id = db.Column(db.Integer(), db.ForeignKey('service.id'),
                           nullable=False)
    service = db.relationship('Service')

    start = db.Column(db.DateTime())

    end = db.Column(db.DateTime())

    description = db.Column(db.Text())

    status = db.Column(ChoiceType(ACTIVITY_STATUS_TYPES))

    confirmed = db.Column(db.Boolean(), default=False)

    created_time = db.Column(db.DateTime(), default=datetime.datetime.utcnow)


class Location(db.Model):
    LOCATION_TYPE = (
        ('0', 'User Location'),
        ('1', 'Fixed Location')
    )
    id = db.Column(db.Integer(), primary_key=True)
    country = db.Column(db.String(), nullable=False)
    area = db.Column(db.String())
    state = db.Column(db.String())
    city = db.Column(db.String())
    street = db.Column(db.String())
    building = db.Column(db.String())
    apartment = db.Column(db.Integer())
    longitude = db.Column(db.Float(), nullable=False)
    latitude = db.Column(db.Float(), nullable=False)

    type = db.Column(ChoiceType(LOCATION_TYPE), default='0')

    def get_name(self):
        location_parts = []
        if self.street:
            street = ' ' + self.street
            if self.building:
                street += ' ' + self.building
                if self.apartment:
                    street += '/' + self.apartment
            location_parts.append(street)

        if self.city:
            location_parts.append(self.city)

        if self.state:
            location_parts.append(self.state)

        location_parts.append(self.country)

        return ', '.join(location_parts)


class OrgCategory(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(256), nullable=False, unique=True)


class Message(db.Model):
    id = db.Column(db.Integer(), primary_key=True)

    from_user_id = db.Column(db.Integer(), db.ForeignKey('users.id'),
                             nullable=False)
    from_user = db.relationship('User', foreign_keys=[from_user_id],
                                backref="from_messages")

    to_user_id = db.Column(db.Integer(), db.ForeignKey('users.id'),
                           nullable=False)
    to_user = db.relationship('User', foreign_keys=[to_user_id],
                              backref="to_messages")

    subject = db.Column(db.String(length=1000), nullable=False)

    text = db.Column(db.Text(), nullable=False)

    service_id = db.Column(db.Integer(), db.ForeignKey('service.id'))
    service = db.relationship('Service')

    created_time = db.Column(db.DateTime(), default=datetime.datetime.utcnow)


class OrderPost(db.Model):
    PRICE_TYPE = (
        ('0', 'Fixed'),
        ('1', 'Hourly'),
        ('2', 'By appointment')
    )

    SPECIALIST_TYPE = (
        ('0', 'Any'),
        ('1', 'Experienced'),
        ('2', 'The most experienced')
    )

    id = db.Column(db.Integer(), primary_key=True)

    author_id = db.Column(db.Integer(), db.ForeignKey('users.id'),
                          nullable=False)
    author = db.relationship('User', foreign_keys=[author_id],
                             backref="order_posts")

    service_id = db.Column(db.Integer(), db.ForeignKey('service.id'),
                           nullable=False)
    service = db.relationship('Service')

    title = db.Column(db.String(), nullable=False)

    description = db.Column(db.Text(), nullable=False)

    price_type = db.Column(ChoiceType(PRICE_TYPE), default='2')

    currency_type = db.Column(CurrencyType)

    price = db.Column(db.Float())

    specialist_type = db.Column(ChoiceType(SPECIALIST_TYPE), default='0')

    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    location = db.relationship('Location')

    created_time = db.Column(db.DateTime(), default=datetime.datetime.utcnow)

    timing_type = db.Column(ChoiceType(TIMING_TYPE), default='0')


class ChatMessage(db.Model):
    id = db.Column(db.Integer(), primary_key=True)

    author_id = db.Column(db.Integer(), db.ForeignKey('users.id'),
                          nullable=False)
    author = db.relationship('User', foreign_keys=[author_id],
                             backref="chat_messages")

    text = db.Column(db.String(), nullable=False)

    room = db.Column(db.String(), nullable=False)

    created_time = db.Column(db.DateTime(), default=datetime.datetime.utcnow)

    edited = db.Column(db.Boolean(), default=False)