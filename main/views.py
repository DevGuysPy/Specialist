# -*- encoding: utf-8 -*-

from flask import render_template, request
from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired

from back_end import app, db
from .models import Specialist, Service


@app.route('/')
def index():
    # s1 = Specialist(name="Vasya", email='vasya@santechnika.net')
    # s2 = Specialist(name="Kolya", email='kolya@elektromerezhi.com.ua')
    # db.session.add(s1)
    # db.session.add(s2)
    # service1 = Service(title=u"Сантехника", domain=u"Дом. работы")
    # service2 = Service(title=u"Электрика", domain=u"Дом. работы")
    # db.session.add(service1)
    # db.session.add(service2)
    # s1 = Specialist.query.filter(Specialist.name == 'Vasya')[0]
    # service1 = Service.query.filter(Service.title == u"Сантехника")
    # s2 = Specialist.query.filter(Specialist.name == 'Kolya')[0]
    # service2 = Service.query.filter(Service.title == u"Электрика")
    # s1.services.append(service1[0])
    # s2.services.append(service2[0])
    # db.session.add(s1)
    # db.session.add(s2)
    # db.session.commit()
    return render_template('index.html')


class SearchForm(Form):
    query = StringField('query', validators=[DataRequired()])


@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        service_name = form.query.data
        specialists = Specialist.query \
            .join(Specialist.services) \
            .filter(Service.title == service_name)
    else:
        specialists = []

    ctx = {
        'form': form,
        'specialists': specialists,
    }
    return render_template('search.html',
                           **ctx)


@app.route('/specialist/<int:specialist_id>/profile')
def specialist_profile(specialist_id):
    return render_template('specialist/profile.html')
