# -*- encoding: utf-8 -*-

import json

from flask import render_template, url_for, flash, request, jsonify
from app import app, cache, db
from .models import Specialist, Service, ServiceActivity, Customer, SpecialistService

from utils import generate_confirmation_token, confirm_token, send_email, get_model_column_values
from forms import SearchForm, AddServiceActivityForm, SpecialistForm

import settings


@app.route('/')
def index():
    all_customers = Customer.query.all()
    return render_template('index.html', all_customers=all_customers)


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
            new_specialist = Specialist(username=form.username.data,
                                        first_name=form.first_name.data,
                                        last_name=form.last_name.data,
                                        password=form.password.data,
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
        db.session.add(new_service)

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

    if request.method == 'POST' and form.validate():
        specialist = Specialist.query.get(form.specialist_id.data)
        customer = Customer.query.get(form.customer_id.data)
        service = Service.query.get(form.service_id.data)

        activity, created = ServiceActivity.get_or_create(
            specialist=specialist,
            customer=customer,
            service=service,
            start=form.start.data,
            defaults={
                'end': form.end.data,
                'description': form.description.data
            })

        if not activity.confirmed:
            token = generate_confirmation_token(activity.id)
            confirm_url = url_for('confirm_specialist_activity',
                                  token=token, _external=True)

            send_email(to=specialist.email,
                       subject='You have been invited by {}'.format(
                           specialist.name),
                       template=settings.CONFIRM_ACTIVITY_HTML.format(
                           service=service.title.encode('utf-8'),
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

    @cache.cached(key_prefix='service_activity_data')
    def get_data():
        with app.test_request_context():
            specialists = get_model_column_values(
                Specialist,
                columns=[
                    {
                        'dict_key': 'id', 'column': 'id'
                    },
                    {
                        'dict_key': 'name', 'column': 'name'
                    }
                ])
            customers = get_model_column_values(
                Customer,
                columns=[
                    {
                        'dict_key': 'id', 'column': 'id'
                    },
                    {
                        'dict_key': 'name', 'column': 'name'
                    }
                ])
            services = get_model_column_values(
                Service,
                columns=[
                    {
                        'dict_key': 'id', 'column': 'id'
                    },
                    {
                        'dict_key': 'name', 'column': 'title'
                    }
                ])
            return {
                'specialists': json.dumps(specialists),
                'customers': json.dumps(customers),
                'services': json.dumps(services)
            }

    context = {
        'form': form,
        'data': get_data()
    }

    return render_template("ServiceActivity.html", **context)
