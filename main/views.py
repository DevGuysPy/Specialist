# -*- encoding: utf-8 -*-
import json

from flask import render_template, url_for, jsonify, redirect, request,\
    session
from flask_views.base import TemplateView
from flask_views.edit import FormView
from sqlalchemy.orm.exc import NoResultFound
from flask.ext.login import login_user, current_user, login_required

from app import app, db

from models import Specialist, Service, UserUserActivity, Company, User,\
    SpecialistService
from utils import generate_confirmation_token, send_email,\
    get_model_column_values, send_user_verification_email, page_not_found, account_not_found
from forms import AddServiceActivityForm, RegistrationForm,\
    SpecialistForm, ServiceForm, LoginForm


@app.route('/')
def index():
    return render_template('index.html')


class CompanyProfile(TemplateView):
    template_name = 'company/Profile.html'

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

        return context

    def get_company(self, kwargs):
        self.org = Company.query.get(kwargs.get('company_id'))
        return self.org


app.add_url_rule(
    '/company/<int:company_id>/profile',
    view_func=CompanyProfile.as_view('company_profile')
)


class UserProfile(TemplateView):
    template_name = 'user/Profile.html'

    def __init__(self):
        super(UserProfile, self).__init__()
        self.user = None

    def get(self, *args, **kwargs):
        self.user = User.query.get(kwargs.get('user_id'))
        if not self.user:
            return account_not_found()

        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(UserProfile, self).get_context_data()
        context.update({'user': self.user})
        context.update({'current_user': current_user})
        # context.update({'activity': self.get_activity(kwargs)})
        context.update({'session': session})
        context.update({'form': self.get_service_activity_form()})

        return context

    def get_service_activity_form(self):
        if self.user.specialist:
            return AddServiceActivityForm.get_form(self.user.specialist)

    # commented for now(will be done soon)
    # def get_activity(self, kwargs):
    #     if self.user is not None:
    #         if self.user.specialist is not None:
    #             self.activity = UserUserActivity.query.filter_by(
    #                 from_user_id=kwargs.get('user_id')).all()
    #         else:
    #             self.activity = UserUserActivity.query.filter_by(
    #                 to_user_id=kwargs.get('user_id')).all()
    #         return self.activity

app.add_url_rule(
    '/account/<int:user_id>',
    view_func=UserProfile.as_view('user_profile')
)


@app.route('/specialist/<int:user_id>/add_service_activity',
           methods=['POST'])
@login_required
def add_service_activity(user_id):
    user = User.query.filter(User.id == int(user_id)).first()
    if not user or not user.specialist:
        return jsonify({
            'status': 'error',
            'errors': 'User is not a specialist'
        })
    form = AddServiceActivityForm.get_form(user.specialist)

    if form.validate():
        activity, created = UserUserActivity.get_or_create(
            from_user=user,
            to_user=current_user,
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
            html = render_template(
                "ConfirmActivityEmail.html",
                service=form.service.data.title.encode('utf-8'),
                start=form.start.data,
                end=form.end.data or "Not specified",
                description=form.description.data or "Not specified",
                confirm_url=str(confirm_url))

            send_email(to=user.email,
                       subject='You have been invited by {}'.format(
                           current_user.full_name()),
                       template=html)

        return jsonify({
            'status': 'ok'
        })

    return jsonify({
        'status': 'error',
        'errors': form.errors
    })


class SignUpView(TemplateView):
    template_name = "Registration.html"

    def get(self, *args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for('user_profile', user_id=current_user.id))

        context = self.get_context_data()
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(SignUpView, self).get_context_data(**kwargs)
        context.update({'basic_form': RegistrationForm()})
        context.update({'session': session})

        return context


app.add_url_rule(
    '/sign_up',
    view_func=SignUpView.as_view('sign_up')
)


@app.route('/user_sign_up', methods=['POST'])
def sign_up_user():
    form = RegistrationForm()
    if form.validate():
        user = User(first_name=form.full_name.data.split(' ')[0],
                    last_name=' '.join(
                        form.full_name.data.split(' ')[1:]),
                    email=form.email.data,
                    password=form.password.data)

        db.session.add(user)
        db.session.flush()

        send_user_verification_email(user.id)

        session['signing_up_user_id'] = user.id

        return jsonify({
            'status': 'ok',
            'user_id': user.id
        })

    return jsonify({
        'status': 'error',
        'errors': form.errors
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


@app.route('/add_service', methods=['POST'])
@login_required
def add_service():
    form = ServiceForm()
    if form.validate():
        service = Service(
            title=form.title.data,
            domain=form.domain.data,
            description=form.description.data)
        db.session.add(service)
        db.session.flush()
        spec_service = SpecialistService(
            specialist_id=current_user.specialist.id,
            service_id=service.id)
        db.session.add(spec_service)
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


@app.route('/add_specialist_service', methods=['POST'])
@login_required
def add_searched_services():
    services = []
    for service_id in json.loads(request.data).get('selected_service_ids', []):
        service = Service.query.filter_by(id=service_id).first()
        if not service:
            return jsonify({
                'status': 'error',
            })

        if service not in current_user.specialist.services.all():
            services.append({
                'name': service.title,
                'id': service_id
            })

            spec_service = SpecialistService(
                specialist_id=current_user.specialist.id,
                service_id=service_id)
            db.session.add(spec_service)

    return jsonify({
        'status': 'ok',
        'services': services
    })


@app.route('/create_specialist', methods=['POST'])
@login_required
def create_specialist():
    form = SpecialistForm()
    if form.validate():
        current_user.phone_number = form.phone.data
        specialist = Specialist(
            user=current_user,
            description=form.description.data,
            experience=form.experience.data)

        db.session.add(specialist)

        return jsonify({
            'status': 'ok'
        })

    return jsonify({
        'status': 'error',
        'errors': form.errors
    })


class LoginView(FormView):
    form_class = LoginForm
    template_name = 'Login.html'
    
    def get(self, *args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for('user_profile', user_id=current_user.id))
        return super(LoginView, self).get(*args, **kwargs)

    def form_invalid(self, form):
        return jsonify({
            'status': 'error',
            'errors': form.errors
        })

    def form_valid(self, form):
        try:
            user = User.query.filter(
                User.email == form.email.data).one()
        except NoResultFound:
            return jsonify({
                'status': 'error',
                'errors': {
                    'password':
                        'User with entered email and password does not exist'
                }
            })

        if user.password != form.password.data:
            return jsonify({
                'status': 'error',
                'errors': {
                    'password':
                        'User with entered email and password does not exist'
                }
            })

        if not user.confirmed:
            return jsonify({
                'status': 'error',
                'errors': {
                    'password':
                        'Confirm your email to log in'
                },
                'send_confirmation_email_url':
                    url_for('send_user_verification_email', user_id=user.id)
            })

        login_user(user)

        if 'next' in request.args:
            next_url = request.args['next']
        else:
            next_url = url_for('user_profile', user_id=user.id)

        return jsonify({
            'status': 'ok',
            'login_success_url': next_url
        })


app.add_url_rule(
    '/login',
    view_func=LoginView.as_view('login')
)


class AccountSpecialist(TemplateView):
    template_name = 'user/AccountSettingsSpecialist.html'
    decorators = [login_required]

    def get(self, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(AccountSpecialist, self).get_context_data()
        context.update({'user': current_user})
        context.update({'spec_form': SpecialistForm()})
        context.update({'ser_form': ServiceForm()})

        return context


app.add_url_rule(
    '/account/specialist',
    view_func=AccountSpecialist.as_view('account_specialist')
)


class AccountCompany(TemplateView):
    template_name = 'user/AccountSettingsCompany.html'
    decorators = [login_required]

    def get(self, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(AccountCompany, self).get_context_data()
        context.update({'user': current_user})
        return context

app.add_url_rule(
    '/account/company',
    view_func=AccountCompany.as_view('account_company')
)


class AccountConfiguration(TemplateView):
    template_name = 'user/AccountSettingsConfiguration.html'
    decorators = [login_required]

    def get(self, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(AccountConfiguration, self).get_context_data()
        context.update({'user': current_user})
        return context

app.add_url_rule(
    '/account/settings',
    view_func=AccountConfiguration.as_view('account_settings')
)


class AccountOffers(TemplateView):
    template_name = 'user/AccountSettingsOffers.html'
    decorators = [login_required]

    def get(self, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(AccountOffers, self).get_context_data()
        context.update({'user': current_user})
        return context

app.add_url_rule(
    '/account/offers',
    view_func=AccountOffers.as_view('account_offers')
)


class AccountOrders(TemplateView):
    template_name = 'user/AccountSettingsOrders.html'
    decorators = [login_required]

    def get(self, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(AccountOrders, self).get_context_data()
        context.update({'user': current_user})
        return context

app.add_url_rule(
    '/account/orders',
    view_func=AccountOrders.as_view('account_orders')
)
