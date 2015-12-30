# -*- encoding: utf-8 -*-
import json

from flask import render_template, url_for, flash, request
from app import app, cache
from .models import Specialist, Service, ServiceActivity, Customer
from utils import generate_confirmation_token, confirm_token, send_email, get_model_column_values
from forms import SearchForm, AddServiceActivityForm
import settings


@app.route('/')
def index():
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
