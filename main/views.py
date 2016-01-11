# -*- encoding: utf-8 -*-
from flask import render_template, url_for, flash, jsonify, redirect, request,\
    session
from flask_views.base import TemplateView
import json
from app import app, db
from flask_json_multidict import get_json_multidict
import settings
from models import Specialist, Service, UserUserActivity, Company, User,\
    SpecialistService
from utils import generate_confirmation_token, confirm_token,\
    send_email, get_model_column_values
from forms import SearchForm, AddServiceActivityForm, RegistrationForm,\
    SpecialistForm, ServiceForm


@app.route('/')
def index():
    # cm = Company(name=u"Kantora", logo=u"1.png")
    # db.session.add(cm)
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
        if self.user is not None:
            context.update({'specialist': self.user.specialist})
            if self.user.specialist is not None:
                context.update({'form': AddServiceActivityForm.get_form(
                    self.user.specialist)})
            else:
                pass
        else:
            pass
        context.update({'activity': self.get_activity(kwargs)})



        return context

    def get_user(self, kwargs):
        self.user = User.query.get(kwargs.get('user_id'))
        return self.user

    def get_activity(self, kwargs):
        if self.user.specialist is not None:
            self.activity = UserUserActivity.query.filter_by(
                from_user_id=kwargs.get('user_id')).all()
        else:
            self.activity = UserUserActivity.query.filter_by(
                to_user_id=kwargs.get('user_id')).all()
        return self.activity


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


@app.route('/user/confirm/<token>')
def confirm_user(token):
    user_id = confirm_token(token)
    user = User.query.filter_by(
        id=user_id).first_or_404()
    user.confirmed = True
    return redirect(url_for('user_profile', user_id=user.id))


@app.route('/sign_up', methods=['GET', 'POST'])
def basic_registration():
    basic_form = RegistrationForm()
    spec_form = SpecialistForm()
    ser_form = ServiceForm()
    if request.method == 'GET':
        return render_template("Registration.html",
                               basic_form=basic_form,
                               spec_form=spec_form,
                               ser_form=ser_form)

    if basic_form.validate():
        user = User(username=basic_form.username.data,
                    first_name=basic_form.full_name.data.split(' ')[0],
                    last_name=' '.join(basic_form.full_name.data.split(' ')[1:]),
                    email=basic_form.email.data,
                    password=basic_form.password.data)

        db.session.add(user)
        db.session.flush()

        token = generate_confirmation_token(user.id)
        confirm_url = url_for('confirm_user',
                              token=token, _external=True)
        send_email(to=user.email,
                   subject='Please confirm your account',
                   template=settings.CONFIRM_USER_HTML.format(
                       full_name=user.full_name(),
                       confirm_url=str(confirm_url)))

        session['signing_up_user_id'] = user.id

        return jsonify({
            'status': 'ok',
            'user_id': user.id
        })
    else:
        return jsonify({
            'status': 'error',
            'errors': basic_form.errors
        })


@app.route('/_get_services_sign_up')
def get_services_data():
    services = get_model_column_values(
        Service,
        columns=[
            {
                'dict_key': 'name', 'column': 'title'
            },
            {
                'dict_key': 'id', 'column': 'id'
            }
        ])
    return jsonify({
        'services': services
    })


@app.route('/spec_sign_up', methods=['POST'])
def sign_up_specialist():
    form = SpecialistForm()
    if form.validate():
        user = User.query.get(session['signing_up_user_id'])
        user.phone_number = form.phone.data
        if user.specialist is None:
            specialist = Specialist(user=user, experience=form.experience.data)
            db.session.add(specialist)
            db.session.flush()
            for service_id in request.form.get('services').split(','):
                spec_service = SpecialistService(
                    specialist_id=specialist.id,
                    service_id=int(service_id))
                db.session.add(spec_service)

        return jsonify({
            'status': 'ok',
            'user_id': user.id
        })

    return jsonify({
        'status': 'error',
        'errors': form.errors
    })


@app.route('/add_service', methods=['POST'])
def add_service():
    form = ServiceForm()
    if form.validate():
        service = Service(
            title=form.title.data,
            domain=form.domain.data,
            description=form.description.data)
        db.session.add(service)
        db.session.flush()
        return jsonify({
            'status': 'ok',
            'service': {
                'name': service.title,
                'id': service.id
            }
        })

    return jsonify({
        'status': 'error',
        'errors': form.errors
    })
