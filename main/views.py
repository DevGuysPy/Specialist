# -*- encoding: utf-8 -*-
from flask import render_template, url_for, flash, jsonify
from flask_views.base import TemplateView

from app import app

import settings
from models import Specialist, Service, ServiceActivity, Customer, Company
from utils import generate_confirmation_token, confirm_token,\
    send_email
from forms import SearchForm, AddServiceActivityForm


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/company/<int:company_id>/profile')
def company_profile(company_id):
    company = Company.query.filter_by(id=company_id).first()
    return render_template('company/profile.html', company=company)


@app.route('/customer/<int:customer_id>/profile')
def customer_profile(customer_id):
    uzver = Customer.query.filter_by(id=customer_id).first()
    return render_template('customer/profile.html', uzver=uzver)


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


class SpecialistProfile(TemplateView):
    template_name = 'specialist/profile.html'

    def __init__(self):
        super(SpecialistProfile, self).__init__()
        self.specialist = None

    def get(self, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(SpecialistProfile, self).get_context_data()
        context.update({'specialist': self.get_specialist(kwargs)})
        context.update({'form': AddServiceActivityForm.get_form(self.specialist)})

        return context

    def get_specialist(self, kwargs):
        self.specialist = Specialist.query.get(kwargs.get('specialist_id'))
        return self.specialist


app.add_url_rule(
    '/specialist/<int:specialist_id>/profile',
    view_func=SpecialistProfile.as_view('specialist_profile')
)


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