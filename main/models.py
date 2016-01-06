import datetime
from app import db
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy_utils import URLType


class AbstractUser(object):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(12))
    email = db.Column(db.String(), nullable=False, unique=True)
    photo = db.Column(db.String(), unique=True)


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


class Specialist(AbstractUser, db.Model):
    experience = db.Column(db.Integer())
    description = db.Column(db.Text())
    services = db.relationship('Service',
                               secondary="specialist_service",
                               lazy='dynamic')
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'),
                           nullable=True)
    company = db.relationship('Company')

    location_id = db.Column(db.Integer, db.ForeignKey('location.id'),
                            nullable=True)
    location = db.relationship('Location')

    registration_time = db.Column(db.DateTime(),
                                  default=datetime.datetime.utcnow)

    confirmed = db.Column(db.Boolean(), default=False)


class Service(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    domain = db.Column(db.String(256), nullable=False)
    # specialists = db.relationship(Specialist)


class Customer(AbstractUser, db.Model):
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'),
                            nullable=True)
    location = db.relationship('Location')

    registration_time = db.Column(db.DateTime(),
                                  default=datetime.datetime.utcnow)

    confirmed = db.Column(db.Boolean(), default=False)


class ServiceActivity(db.Model):
    id = db.Column(db.Integer(), primary_key=True)

    specialist_id = db.Column(db.Integer(), db.ForeignKey('specialist.id'),
                              nullable=False)
    specialist = db.relationship('Specialist')

    customer_id = db.Column(db.Integer(), db.ForeignKey('customer.id'),
                            nullable=False)
    customer = db.relationship('Customer')

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
                      specialist,
                      customer,
                      service,
                      start,
                      defaults=None):
        """
        Func for adding ServiceActivity

        :param Specialist specialist: specialist
        :param Customer customer: customer
        :param Service service: service
        :param int start: start
        :param dict defaults: defaults
        :return :
        """

        try:
            activity = ServiceActivity.query.filter_by(
                specialist=specialist, customer=customer,
                service=service, start=start).one()
            return activity, False
        except NoResultFound:
            activity = ServiceActivity(
                specialist=specialist, customer=customer,
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