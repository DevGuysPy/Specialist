import datetime
from app import db
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy_utils import URLType, ChoiceType


class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)

    username = db.Column(db.String(256), nullable=False)

    first_name = db.Column(db.String(256))

    last_name = db.Column(db.String(256))

    phone = db.Column(db.String(12))

    email = db.Column(db.String(), nullable=False, unique=True)

    photo = db.Column(db.String(), unique=True)

    location_id = db.Column(db.Integer, db.ForeignKey('location.id'),
                            nullable=True)
    location = db.relationship('Location')

    specialist = db.relationship("Specialist",
                                 uselist=False, back_populates="user")

    registration_time = db.Column(db.DateTime(),
                                  default=datetime.datetime.utcnow)

    confirmed = db.Column(db.Boolean(), default=False)


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

    category_id = db.Column(db.Integer(), db.ForeignKey('org_category.id'),
                            nullable=True)
    category = db.relationship('OrgCategory')

    location_id = db.Column(db.Integer, db.ForeignKey('location.id'),
                            nullable=True)
    location = db.relationship('Location')

    created_time = db.Column(db.DateTime(),
                             default=datetime.datetime.utcnow)

    confirmed = db.Column(db.Boolean(), default=False)


class Specialist(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", back_populates="specialist")

    experience = db.Column(db.Integer())

    description = db.Column(db.Text())

    services = db.relationship('Service',
                               secondary="specialist_service",
                               lazy='dynamic')

    org_id = db.Column(db.Integer, db.ForeignKey('company.id'),
                       nullable=True)
    org = db.relationship('Company')

    confirmed = db.Column(db.Boolean(), default=False)


class Service(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    domain = db.Column(db.String(256), nullable=False)
    # specialists = db.relationship(Specialist)


class UserUserActivity(db.Model):
    id = db.Column(db.Integer(), primary_key=True)

    from_user_id = db.Column(db.Integer(), db.ForeignKey('user.id'),
                             nullable=False)
    from_user = db.relationship('User', foreign_keys=[from_user_id])

    to_user_id = db.Column(db.Integer(), db.ForeignKey('user.id'),
                           nullable=False)
    to_user = db.relationship('User', foreign_keys=[to_user_id])

    service_id = db.Column(db.Integer(), db.ForeignKey('service.id'),
                           nullable=False)
    service = db.relationship('Service')

    start = db.Column(db.DateTime())
    end = db.Column(db.DateTime())
    description = db.Column(db.Text())

    specialist_rating = db.Column(db.Integer())
    customer_rating = db.Column(db.Integer())

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
        Func for adding UserUserActivity

        :param User from_user: specialist
        :param User to_user: customer
        :param Service service: service
        :param int start: start
        :param dict defaults: defaults
        :return :
        """

        try:
            activity = UserUserActivity.query.filter_by(
                from_user=from_user, to_user=to_user,
                service=service, start=start).one()
            return activity, False
        except NoResultFound:
            activity = UserUserActivity(
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


class UserOrgActivity(db.Model):
    ACTIVITY_TYPE = (
        (0, 'User Org'),
        (1, 'Org User')
    )

    id = db.Column(db.Integer(), primary_key=True)

    org_id = db.Column(db.Integer(), db.ForeignKey('company.id'),
                       nullable=False)
    org = db.relationship('Company', foreign_keys=[org_id])

    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'),
                        nullable=False)
    user = db.relationship('User', foreign_keys=[user_id])

    service_id = db.Column(db.Integer(), db.ForeignKey('service.id'),
                           nullable=False)
    service = db.relationship('Service')

    customer = db.Column(ChoiceType(ACTIVITY_TYPE), default=0)

    start = db.Column(db.DateTime())
    end = db.Column(db.DateTime())
    description = db.Column(db.Text())

    confirmed = db.Column(db.Boolean(), default=False)

    created_time = db.Column(db.DateTime(), default=datetime.datetime.utcnow)


class OrgOrgActivity(db.Model):
    id = db.Column(db.Integer(), primary_key=True)

    from_org_id = db.Column(db.Integer(), db.ForeignKey('company.id'),
                            nullable=False)
    from_org = db.relationship('Company', foreign_keys=[from_org_id])

    to_org_id = db.Column(db.Integer(), db.ForeignKey('company.id'),
                          nullable=False)
    to_org = db.relationship('Company', foreign_keys=[to_org_id])

    service_id = db.Column(db.Integer(), db.ForeignKey('service.id'),
                           nullable=False)
    service = db.relationship('Service')

    start = db.Column(db.DateTime())
    end = db.Column(db.DateTime())
    description = db.Column(db.Text())

    confirmed = db.Column(db.Boolean(), default=False)

    created_time = db.Column(db.DateTime(), default=datetime.datetime.utcnow)


class Location(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    country = db.Column(db.String(), nullable=False)
    city = db.Column(db.String())
    street = db.Column(db.String())
    building = db.Column(db.String())
    apartment = db.Column(db.Integer())


class OrgCategory(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(256), nullable=False, unique=True)