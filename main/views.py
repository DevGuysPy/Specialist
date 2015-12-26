# -*- encoding: utf-8 -*-
from flask import render_template, url_for, flash
from back_end import app
from app import session
from .models import Specialist, Service, ServiceActivity
from utils import generate_confirmation_token, confirm_token, send_email
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


@app.route('/confirm_specialist_activity/<token>')
def confirm_specialist_activity(token):
    activity_id = confirm_token(token)
    activity = ServiceActivity.query.filter_by(id=activity_id).first_or_404()
    if activity.confirmed:
        msg = 'Activity already confirmed.'
    else:
        activity.confirmed = True
        session.commit()
        msg = 'You have confirmed your relationship with {}.'.format(activity.specialist.name)
    return render_template('confirm.html', msg=msg)


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
                           start=form.start.data or "Not specified",
                           end=form.end.data or "Not specified",
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
