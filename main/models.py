from app import db


class AbstractUser(object):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(12))
    email = db.Column(db.String(), nullable=False, unique=True)
    photo = db.Column(db.String(), unique=True, nullable=True)


class SpecialistService(db.Model):
    __tablename__ = 'specialist_service'
    specialist_id = db.Column(db.Integer(), db.ForeignKey('specialist.id'),
                              primary_key=True)
    service_id = db.Column(db.Integer(),  db.ForeignKey('service.id'),
                           primary_key=True)


class Specialist(AbstractUser, db.Model):
    experience = db.Column(db.Integer())
    description = db.Column(db.Text())
    services = db.relationship('Service', secondary="specialist_service")


class Service(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    domain = db.Column(db.String(256), nullable=False)
    # specialists = db.relationship(Specialist)


class Customer(AbstractUser, db.Model):
    pass


class ServiceActivity(db.Model):
    id = db.Column(db.Integer(), primary_key=True)

    specialist_id = db.Column(db.Integer(), db.ForeignKey('specialist.id'), nullable=False)
    specialist = db.relationship('Specialist')

    customer_id = db.Column(db.Integer(), db.ForeignKey('customer.id'), nullable=False)
    customer = db.relationship('Customer')

    service_id = db.Column(db.Integer(), db.ForeignKey('service.id'), nullable=False)
    service = db.relationship('Service')

    start = db.Column(db.DateTime())
    end = db.Column(db.DateTime())
    description = db.Column(db.Text())

    specialist_rating = db.Column(db.Integer())
    customer_rating = db.Column(db.Integer())


class Location(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    country = db.Column(db.String(), nullable=False)
    city = db.Column(db.String())
    street = db.Column(db.String())
    building = db.Column(db.String())
    appartment = db.Column(db.Integer())
