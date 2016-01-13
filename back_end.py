# -*- encoding: utf-8 -*-
import random
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

from app import app, db
from main.models import Service, Specialist, Company

manager = Manager(app)
manager.add_command('db', MigrateCommand)
migrate = Migrate(app, db)


@manager.command
def rr():
    db.drop_all()
    db.create_all()


if __name__ == '__main__':
    manager.run()
