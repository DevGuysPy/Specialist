# -*- encoding: utf-8 -*-

from flask import render_template, url_for, flash, request, jsonify
from app import app, session, db

from utils import generate_confirmation_token, confirm_token, send_email
from forms import SearchForm, AddServiceActivityForm, SpecialistForm
import settings
from .models import Specialist, Service, ServiceActivity, SpecialistService


@app.route('/')
def index():

    # s1 = Specialist(name="Vasya", email='vasya@santechnika.net')
    # s2 = Specialist(name="Kolya", email='kolya@elektromerezhi.com.ua')
    # db.session.add(s1)
    # db.session.add(s2)
    # service1 = Service(title=u"Гуся", domain=u"Дом. работы")
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


@app.route('/specialist-registration/', methods=['GET', 'POST'])
def specialist_registration():
    all_services = Service.query.all()
    form = SpecialistForm(request.form)
    if request.method == 'POST':
        if form.validate():
            new_specialist = Specialist(name=form.name.data,
                                        email=form.email.data,
                                        phone=form.phone.data,
                                        experience=form.experience.data,
                                        description=form.description.data)

            db.session.add(new_specialist)
            db.session.flush()
            db.session.refresh(new_specialist)

            services_query_identifiers = request.form.getlist('services')
            services_objects = Service.query.filter(
                Service.id.in_(services_query_identifiers)).all()

            for service_object in services_objects:
                service_id = service_object.id
                specialist_service = \
                    SpecialistService(specialist_id=new_specialist.id,
                                      service_id=service_id)
                db.session.add(specialist_service)

            db.session.commit()

            return jsonify({
                'status': 'ok',
            })
        else:
            return jsonify({
                'input_errors': form.errors,
                'status': 'error'
            })

    return render_template("SpecialistRegistration.html", services=all_services,
                           form=form)


@app.route('/service-registration/', methods=['GET', 'POST'])
def service_register():
    if request.method == "POST":
        new_service = Service(title=request.form['title'],
                              domain=request.form['domain'])
        session.add(new_service)

        return render_template("RegisterService.html")

    return render_template("RegisterService.html")


@app.route('/service_activity/confirm/<token>')
def confirm_specialist_activity(token):
    activity_id = confirm_token(token)
    activity = ServiceActivity.query.filter_by(id=activity_id).first_or_404()
    if activity.confirmed:
        flash('Activity already confirmed.')
    else:
        activity.confirmed = True
        flash('You have confirmed your relationship with {}.'.format(
            activity.specialist.name))

    return render_template('ConfirmServiceActivity.html')


@app.route('/service_activity/add', methods=['GET', 'POST'])
def add_service_activity():
    form = AddServiceActivityForm()

    if form.validate_on_submit():

        activity, created = ServiceActivity.get_or_create(
            specialist=form.specialist.data, customer=form.customer.data,
            service=form.service.data, start=form.start.data,
            defaults={
                'end': form.end.data,
                'description': form.description.data
            })

        if not activity.confirmed:
            token = generate_confirmation_token(activity.id)
            confirm_url = url_for('confirm_specialist_activity',
                                  token=token, _external=True)

            send_email(to=form.specialist.data.email,
                       subject='You have been invited by {}'.format(
                           form.specialist.data.name),
                       template=settings.CONFIRM_ACTIVITY_HTML.format(
                           service=form.service.data.title.encode('utf-8'),
                           start=form.start.data,
                           end=form.end.data or "Not specified",
                           description=form.description.data or "Not specified",
                           confirm_url=str(confirm_url)))

            flash('Email was sent successfully')

    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash("Error in the {} field - {}".format(
                    getattr(form, field).label.text,
                    error
                ))

    context = {
        'form': form,
    }

    return render_template("ServiceActivity.html", **context)
