# -*- encoding: utf-8 -*-
import random
import names
from datetime import datetime
import logging
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

from app import app, db
from default_db_data import services_data
from main.models import Service, ServiceCategory, User, UserUserActivity

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

manager = Manager(app)
manager.add_command('db', MigrateCommand)
migrate = Migrate(app, db)


# create users and activities
@manager.command
def create_all():
    for i in range(20):
        i = UserUserActivity(confirmed=True,
                             start=datetime.utcnow(),
                             from_user_id=1,
                             to_user_id=2,
                             service_id=1
                             )
        db.session.add(i)
        db.session.commit()


def create_users():
    for i in range(100):
        full_name = names.get_full_name()
        i = User(first_name=full_name.split(' ')[0],
                 last_name=' '.join(
                         full_name.split(' ')[1:]),
                 email='{}{}@gmail.com'.format(
                         unicode(full_name.split(' ')[0]).lower(),
                         unicode(full_name.split(' ')[1]).lower()),
                 password='1111',
                 confirmed=True)
        db.session.add(i)
        db.session.commit()

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
