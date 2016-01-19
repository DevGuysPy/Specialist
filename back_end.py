# -*- encoding: utf-8 -*-
import logging
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

from app import app, db
from main.models import Service, ServiceCategory
from default_db_data import services_data

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

manager = Manager(app)
manager.add_command('db', MigrateCommand)
migrate = Migrate(app, db)


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
