# -*- encoding: utf-8 -*-
import json

from flask import render_template, url_for, flash
from flask_views.edit import FormView
from app import app, cache

import settings
from models import Specialist, Service, ServiceActivity, Customer
from utils import generate_confirmation_token, confirm_token,\
    send_email, get_model_column_values
from forms import SearchForm, AddServiceActivityForm


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


class AddServiceActivity(FormView):
    form_class = AddServiceActivityForm
    template_name = 'ServiceActivity.html'

    def form_valid(self, form):
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

        return super(AddServiceActivity, self).form_valid(form)
    
    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                flash("Error in the {} field - {}".format(
                    getattr(form, field).label.text,
                    error
                ))

        return super(AddServiceActivity, self).form_invalid(form)

    def get_success_url(self):
        return url_for('add_service_activity')

    def get_context_data(self, **kwargs):
        context = super(AddServiceActivity, self).get_context_data(**kwargs)
        context.update({'typeahead_data': self.get_typeahead_data()})

        return super(AddServiceActivity, self).get_context_data(**context)

    @cache.cached(key_prefix='service_activity_data')
    def get_typeahead_data(self):
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


app.add_url_rule(
    '/service_activity/add',
    view_func=AddServiceActivity.as_view('add_service_activity')
)
