# -*- encoding: utf-8 -*-
import names
import random

from loremipsum import get_sentences

from datetime import datetime, timedelta
import logging

from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

from app import app, db
from default_db_data import services_data, nouns, countries_and_cities
from main.models import (Service, ServiceCategory, User, UserUserActivity,
                         Specialist, SpecialistService, Company, OrgCategory,
                         Location)

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

manager = Manager(app)
manager.add_command('db', MigrateCommand)
migrate = Migrate(app, db)


# create users and activities
@manager.command
def create_activities():
    time = datetime.utcnow()
    for i in range(20):
        i = UserUserActivity(confirmed=True,
                             start=time,
                             from_user_id=1,
                             to_user_id=2,
                             service_id=1
                             )
        db.session.add(i)
        db.session.commit()


@manager.command
def create_all(srv=False, comp=False, usr=False):
    if srv:
        add_services_to_database()
    if comp:
        create_companies()
    if usr:
        create_users()


def get_random_date(from_year, to_year):
    year = random.choice(range(from_year, to_year))
    month = random.choice(range(1, 13))
    day = random.choice(range(1, 29))
    birth_date = datetime(year, month, day)

    return birth_date


@manager.command
def create_users():
    orgs = Company.query.all()
    services = Service.query.all()

    for i in range(1000):
        city_item = random.choice(countries_and_cities)

        location_name = city_item['city'].split(', ')
        if len(location_name) == 2:
            city, country = location_name
            state = None
        elif len(location_name) == 3:
            city, state, country = location_name
        else:
            continue

        latitude, longitude = city_item['ll'].split(',')

        loc = Location(country=country,
                       state=state,
                       city=city,
                       latitude=latitude,
                       longitude=longitude)

        db.session.add(loc)
        db.session.flush()

        first_name, last_name = names.get_full_name().split()
        user = User(first_name=first_name,
                    last_name=last_name,
                    email='{}{}@gmail.com'.format(
                        unicode(first_name.lower()),
                        unicode(last_name.lower()) + str(
                            random.randint(0, 10000))),
                    password='1111',
                    confirmed=True,
                    location=loc,
                    birth_date=get_random_date(1950, 1996),
                    phone_number='+380' + str(
                        random.randint(100000000, 999999999)))

        db.session.add(user)
        db.session.flush()

        spec = Specialist(user=user,
                          org=random.choice(orgs),
                          experience=str(random.randint(0, 11)),
                          confirmed=True,
                          description=' '.join(
                              get_sentences(random.randint(4, 7))))
        db.session.add(spec)
        db.session.flush()

        service_ids = [random.choice(services).id for x in range(20)]
        for ser_id in set(service_ids):
            spec_ser = SpecialistService(
                specialist_id=spec.id, service_id=ser_id)
            db.session.add(spec_ser)

        logger.info('Added user {} {}'.format(i, user.full_name()))

    db.session.commit()


@manager.command
def create_companies():
    def get_name(cls):
        com_name = random.choice(nouns).title()
        if cls.query.filter_by(name=com_name).first():
            return get_name(cls)
        return com_name

    for c_index in range(20):
        cat_name = get_name(OrgCategory)
        cat = OrgCategory(name=cat_name)
        db.session.add(cat)
        logger.info('Added org category {}'.format(cat_name))

    db.session.commit()

    categories = OrgCategory.query.all()
    for index in range(150):
        name = get_name(Company)
        com = Company(name=name, category=random.choice(categories))
        db.session.add(com)
        logger.info('Added company {}'.format(name))

    db.session.commit()

@manager.command
def custom():
    services = Service.query.all()
    ser_id = random.choice(services).id

@manager.command
def rr():
    db.drop_all()
    db.create_all()


@manager.command
def add_services_to_database():
    for category_name, services in services_data.iteritems():
        category = ServiceCategory(title=category_name)
        db.session.add(category)
        db.session.flush()
        logger.info('Added category: {}'.format(category_name))

        for s in services:
            service = Service(title=s, category=category)
            db.session.add(service)
            logger.info('Added service: {}'.format(s))

    db.session.commit()


if __name__ == '__main__':
    manager.run()
