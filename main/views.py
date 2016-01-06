# -*- encoding: utf-8 -*-
from flask import render_template, url_for, flash, jsonify
from flask_views.base import TemplateView

from app import app, db

import settings
from models import Specialist, Service, UserUserActivity, Company, User
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
        # context.update({'specialist': self.get_specialist(kwargs)})

        return context

    def get_company(self, kwargs):
        self.org = Company.query.get(kwargs.get('company_id'))
        return self.org

    # def get_specialist(self, kwargs):
    #     self.specialist = Specialist.query.filter_by(
    #         company_id=kwargs.get('company_id')).all()
    #     return self.specialist


app.add_url_rule(
    '/company/<int:company_id>/profile',
    view_func=CompanyProfile.as_view('company_profile')
)


class UserProfile(TemplateView):
    template_name = 'user/profile.html'

    def __init__(self):
        super(UserProfile, self).__init__()
        self.user = None

    def get(self, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(UserProfile, self).get_context_data()
        context.update({'user': self.get_user(kwargs)})
        context.update({'specialist': self.user.specialist})
        # context.update({'activity': self.get_activity(kwargs)})
        context.update({'form': AddServiceActivityForm.get_form(
            self.user.specialist)})

        return context

    def get_user(self, kwargs):
        self.user = User.query.get(kwargs.get('user_id'))
        return self.user

    # def get_activity(self, kwargs):
    #     self.user = UserUserActivity.query.filter_by(
    #         specialist_id=kwargs.get('specialist_id')).all()
    #     return self.user


app.add_url_rule(
    '/user/<int:user_id>/profile',
    view_func=UserProfile.as_view('user_profile')
)


@app.route('/user_user_activity/confirm/<token>')
def confirm_specialist_activity(token):
    activity_id = confirm_token(token)
    activity = UserUserActivity.query.filter_by(
        id=activity_id).first_or_404()
    if activity.confirmed:
        flash('Activity already confirmed.')
    else:
        activity.confirmed = True
        flash('You have confirmed your relationship with {}.'.format(
            activity.to_user.username))

    return render_template('ConfirmServiceActivity.html')


@app.route('/specialist/<int:specialist_id>/add_service_activity',
           methods=['POST'])
def add_service_activity(specialist_id):
    user = User.query.join(User.specialist).filter(
        Specialist.id == specialist_id).first_or_404()
    if not user.specialist:
        return jsonify({
            'status': 'error',
            'errors': 'User is not specialist'
        })
    form = AddServiceActivityForm.get_form(user.specialist)

    if form.validate():
        activity, created = UserUserActivity.get_or_create(
            from_user=user,
            # temporary (waiting for registration and login)
            to_user=User.query.get(2),
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

            send_email(to=user.email,
                       subject='You have been invited by {}'.format(
                           # temporary (waiting for registration and login)
                           User.query.get(2).username),
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