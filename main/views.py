# -*- encoding: utf-8 -*-
from flask import render_template, url_for, flash, jsonify
from flask_views.base import TemplateView

from app import app, db

import settings
from models import Specialist, Service, ServiceActivity, Customer, Company
from utils import generate_confirmation_token, confirm_token,\
    send_email
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


class CompanyProfile(TemplateView):
    template_name = 'company/profile.html'

    def __init__(self):
        super(CompanyProfile, self).__init__()
        self.org = None
        self.specialist = None

    def get(self, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(CompanyProfile, self).get_context_data()
        context.update({'company': self.get_company(kwargs)})
        context.update({'specialist': self.get_specialist(kwargs)})

        return context

    def get_company(self, kwargs):
        self.org = Company.query.get(kwargs.get('company_id'))
        return self.org

    def get_specialist(self, kwargs):
        self.specialist = Specialist.query.filter_by(company_id=kwargs.get('company_id')).all()
        return self.specialist


app.add_url_rule(
    '/company/<int:company_id>/profile',
    view_func=CompanyProfile.as_view('company_profile')
)


class CustomerProfile(TemplateView):
    template_name = 'customer/profile.html'

    def __init__(self):
        super(CustomerProfile, self).__init__()
        self.customer = None
        self.activity = None

    def get(self, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(CustomerProfile, self).get_context_data()
        context.update({'customer': self.get_customer(kwargs)})
        context.update({'activity': self.get_activity(kwargs)})

        return context

    def get_customer(self, kwargs):
        self.customer = Customer.query.get(kwargs.get('customer_id'))
        return self.customer

    def get_activity(self, kwargs):
        self.activity = ServiceActivity.query.filter_by(customer_id=kwargs.get('customer_id')).all()
        return self.activity

app.add_url_rule(
    '/customer/<int:customer_id>/profile',
    view_func=CustomerProfile.as_view('customer_profile')
)


class SpecialistProfile(TemplateView):
    template_name = 'specialist/profile.html'

    def __init__(self):
        super(SpecialistProfile, self).__init__()
        self.specialist = None
        self.activity = None

    def get(self, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(SpecialistProfile, self).get_context_data()
        context.update({'specialist': self.get_specialist(kwargs)})
        context.update({'activity': self.get_activity(kwargs)})
        context.update({'form': AddServiceActivityForm.get_form(self.specialist)})

        return context

    def get_specialist(self, kwargs):
        self.specialist = Specialist.query.get(kwargs.get('specialist_id'))
        return self.specialist

    def get_activity(self, kwargs):
        self.activity = ServiceActivity.query.filter_by(specialist_id=kwargs.get('specialist_id')).all()
        return self.activity


app.add_url_rule(
    '/specialist/<int:specialist_id>/profile',
    view_func=SpecialistProfile.as_view('specialist_profile')
)


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


@app.route('/specialist/<int:specialist_id>/add_service_activity',
           methods=['POST'])
def add_service_activity(specialist_id):
    specialist = Specialist.query.get(specialist_id)
    form = AddServiceActivityForm.get_form(specialist)

    if form.validate():
        activity, created = ServiceActivity.get_or_create(
            specialist=specialist,
            # temporary (waiting for registration and login)
            customer=Customer.query.get(1),
            service=form.service.data,
            start=form.start.data,
            defaults={
                'end': form.end.data,
                'description': form.description.data
            })

        if not activity.confirmed:
            db.session.flush()
            token = generate_confirmation_token(activity.id)
            confirm_url = url_for('confirm_specialist_activity',
                                  token=token, _external=True)

            send_email(to=specialist.email,
                       subject='You have been invited by {}'.format(
                           specialist.name),
                       template=settings.CONFIRM_ACTIVITY_HTML.format(
                           service=form.service.data.title.encode('utf-8'),
                           start=form.start.data,
                           end=form.end.data or "Not specified",
                           description=form.description.data or "Not specified",
                           confirm_url=str(confirm_url)))

        return jsonify({
            'status': 'ok'
        })
    else:
        return jsonify({
            'status': 'error',
            'errors': form.errors
        })