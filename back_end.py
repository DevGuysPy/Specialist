# -*- encoding: utf-8 -*-
import random
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

from app import app, db
from main.models import Service, Specialist, Customer

manager = Manager(app)
manager.add_command('db', MigrateCommand)
migrate = Migrate(app, db)


@manager.command
def mk_all():
    db.drop_all()
    db.create_all()
    create_all()
    connect_all()


names = ['Vasia', 'Kolia', 'Petia', 'Ivan', 'Roman', 'Andrii', 'Sergii', 'Vova']
services = [u"Сантехника", u"Электрика"]
emails_for_cust = ['yandex.ru', 'gmail.com']
emails_for_spec = ['mail.ru', 'ukr.net']


def create_all():
    for s in services:
        service = Service(title=s, domain=u"Дом. работы")
        db.session.add(service)
        db.session.commit()
    for n in names:
        random_mail = random.randint(0, 1)
        mail_c = emails_for_spec[random_mail]
        mail_s = emails_for_spec[random_mail]
        spec = Specialist(name=n, email='{}@{}'.format(n, mail_s))
        cust = Customer(name=n, email='{}@{}'.format(n, mail_c))
        db.session.add(cust)
        db.session.add(spec)
        db.session.commit()


def connect_all():
    for n in names:
        service_num = random.randint(0, 1)
        service = services[service_num]
        spec = Specialist.query.filter(Specialist.name == n)[0]
        service1 = Service.query.filter(Service.title == service)
        spec.services.append(service1[0])
        db.session.add(spec)
        db.session.commit()


if __name__ == '__main__':
    manager.run()
