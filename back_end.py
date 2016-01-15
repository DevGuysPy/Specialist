# -*- encoding: utf-8 -*-
import random
import names
from datetime import datetime
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

from app import app, db
from main.models import User, UserUserActivity

manager = Manager(app)
manager.add_command('db', MigrateCommand)
migrate = Migrate(app, db)


# # create users and activities
# @manager.command
# def create_all():
#     for i in range(20):
#         i = UserUserActivity(confirmed=True,
#                              start=datetime.utcnow(),
#                              from_user_id=random.randint(0, 99),
#                              to_user_id=random.randint(0, 99),
#                              service_id=2
#                              )
#         db.session.add(i)
#         db.session.commit()
#
#
# def create_users():
#     for i in range(100):
#         full_name = names.get_full_name()
#         i = User(first_name=full_name.split(' ')[0],
#                  last_name=' '.join(
#                          full_name.split(' ')[1:]),
#                  email='{}{}@gmail.com'.format(
#                          unicode(full_name.split(' ')[0]).lower(),
#                          unicode(full_name.split(' ')[1]).lower()),
#                  password='1111',
#                  confirmed=True)
#         db.session.add(i)
#         db.session.commit()
#
#
if __name__ == '__main__':
    manager.run()
