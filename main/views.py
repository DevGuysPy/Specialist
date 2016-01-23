# -*- encoding: utf-8 -*-
import json
from datetime import date
from math import radians, cos, sin, asin, sqrt
from sqlalchemy import desc

from flask import (render_template, url_for, jsonify, redirect, request,
                   session)
from flask_views.base import TemplateView
from flask_views.edit import FormView
from sqlalchemy.orm.exc import NoResultFound
from flask.ext.login import login_user, current_user, login_required

from app import app, db, cache

from models import (Specialist, Service, UserUserActivity, Company, User,
                    SpecialistService, ServiceCategory, Location)
from utils import (generate_confirmation_token, send_email,
                   get_model_column_values, send_user_verification_email,
                   account_not_found, page_not_found)
from forms import (AddServiceActivityForm, RegistrationForm,
                   SpecialistForm, ServiceForm, LoginForm)
from schemas import ServiceSchema, ServiceCategorySchema

current_user_location = None


class Home(TemplateView):
    template_name = 'index.html'

    def __init__(self):
        super(Home, self).__init__()
        self.stats = {}

    def get(self, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(Home, self).get_context_data()
        context.update({'stats': self.get_stats()})

        return context

    def get_stats(self):
        self.stats['activities'] = UserUserActivity.query\
            .filter(UserUserActivity.created_time >= date.today()).count()
        self.stats['specialists'] = len(Specialist.query.all())
        # Coming soon
        #  self.stats['online'] = User.query.filter()
        self.stats['users'] = len(User.query.all())
        self.stats['services'] = len(Service.query.all())

        return self.stats


app.add_url_rule(
    '/',
    view_func=Home.as_view('home')
)


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
                    password=form.password.data,
                    birth_date=form.birth_date.data)

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
    """
    Func for Specialist creation
    :return:
    """

    form = SpecialistForm()
    if form.validate():
        specialist = Specialist(
            user=current_user,
            description=form.description.data,
            experience=form.experience.data)
        db.session.add(specialist)

        # updating DB with Specialist object to make it
        # visible to other transactions
        db.session.flush()

        spec_service = SpecialistService(
            service_id=form.service_id.data,
            specialist_id=specialist.id)
        db.session.add(spec_service)

        # to add location user must select at least his country
        if form.location.country.data:
            location = Location(
                country=form.location.country.data,
                state=form.location.state.data,
                city=form.location.city.data,
                building=form.location.building.data)

            db.session.add(location)
            current_user.location = location

        current_user.phone_number = form.phone.data

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

    def __init__(self):
        super(AccountSpecialist, self).__init__()
        self.user = None

    def get(self, *args, **kwargs):
        self.user = current_user
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(AccountSpecialist, self).get_context_data()
        context.update({'user': current_user})
        context.update({'spec_form': SpecialistForm()})
        context.update({'ser_form': ServiceForm()})
        context.update({
            'latest_activities': self.get_latest_u_u_services_activities()
        })
        context.update({'services_dict': self.get_services_json()})
        context.update({'categories_dict': self.get_categories_json()})

        return context

    def get_latest_u_u_services_activities(self):
        """
        Get latest UserUserActivity for all services offered by the user
        sample_return_dict = {
            'Service Title': UserUserActivity objects
        }
        :return:
        """

        if not self.user.specialist:
            return

        latest_activities = {}
        for service in self.user.specialist.services.all():
            rel = UserUserActivity.query\
                .filter_by(service=service,
                           from_user=self.user,
                           confirmed=True)\
                .order_by(desc(UserUserActivity.start)).first()
            latest_activities[service.title] = rel

        return latest_activities

    @cache.cached(key_prefix='services_dict')
    def get_services_json(self):
        """
        Get all services for js.
        sample_of_return_json = [
            {
                'title': 'Service',
                'id': 1,
                'category_id': 2
            },
            {
                'title': 'Service2',
                'id': 2,
                'category_id': 3
            }
        ]
        :return:
        """

        schema = ServiceSchema(many=True)
        return json.dumps(schema.dump(Service.query.all()).data)

    @cache.cached(key_prefix='categories_dict')
    def get_categories_json(self):
        """
        Get all categories for js.
        sample_of_return_json = [
            {
                'title': 'Category',
                'id': 1
            },
            {
                'title': 'Category2',
                'id': 2
            },
        ]
        :return:
        """

        schema = ServiceCategorySchema(many=True)
        return json.dumps(schema.dump(ServiceCategory.query.all()).data)


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

    def __init__(self):
        super(AccountOffers, self).__init__()

    def get(self, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(AccountOffers, self).get_context_data()
        context.update({'user': current_user})
        context.update({'active_offers': self.get_active_offers()})
        context.update({'past_offers': self.get_past_offers()})

        return context

    def get_active_offers(self):
        active_offers = UserUserActivity.query\
            .filter(
                UserUserActivity.from_user_id == current_user.id,
                UserUserActivity.start >= date.today())\
            .order_by(UserUserActivity.start.desc()).all()

        return active_offers

    def get_past_offers(self):
        past_offers = UserUserActivity.query\
            .filter(
                UserUserActivity.from_user_id == current_user.id,
                UserUserActivity.start < date.today())\
            .order_by(UserUserActivity.start.desc()).all()

        return past_offers

app.add_url_rule(
    '/account/offers',
    view_func=AccountOffers.as_view('account_offers')
)


class AccountOrders(TemplateView):
    template_name = 'user/AccountSettingsOrders.html'
    decorators = [login_required]

    def __init__(self):
        super(AccountOrders, self).__init__()

    def get(self, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(AccountOrders, self).get_context_data()
        context.update({'user': current_user})
        context.update({'active_orders': self.get_active_orders()})
        context.update({'past_orders': self.get_past_orders()})

        return context

    def get_active_orders(self):
        active_orders = UserUserActivity.query\
            .filter(
                UserUserActivity.to_user_id == current_user.id,
                UserUserActivity.start >= date.today())\
            .order_by(UserUserActivity.start.desc()).all()

        return active_orders

    def get_past_orders(self):
        past_orders = UserUserActivity.query\
            .filter(
                UserUserActivity.to_user_id == current_user.id,
                UserUserActivity.start < date.today())\
            .order_by(UserUserActivity.start.desc()).all()
        return past_orders

app.add_url_rule(
    '/account/orders',
    view_func=AccountOrders.as_view('account_orders')
)


class AccountOffer(TemplateView):
    template_name = 'user/AccountOffer.html'
    decorators = [login_required]

    def get(self, *args, **kwargs):
        self.activity = UserUserActivity.query.get(kwargs.get('id'))
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(AccountOffer, self).get_context_data()
        context.update({'user': current_user})
        context.update({'activity': self.activity})
        return context


app.add_url_rule(
    '/account/offer/<int:id>',
    view_func=AccountOffer.as_view('offer')
)


class AccountOrder(TemplateView):
    template_name = 'user/AccountOrder.html'
    decorators = [login_required]

    def get(self, *args, **kwargs):
        self.activity = UserUserActivity.query.get(kwargs.get('id'))
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(AccountOrder, self).get_context_data()
        context.update({'user': current_user})
        context.update({'activity': self.activity})
        return context


app.add_url_rule(
    '/account/order/<int:id>',
    view_func=AccountOrder.as_view('order')
)


@app.route('/autocomplete/services')
def service_autocomplete():
    if 'query' not in request.args:
        return page_not_found()

    query = request.args['query']

    search_string = query.strip()

    try:
        # db query which selects services which start with search string.
        # Order by count of UserUserActivity entries.
        services = db.session\
            .query(Service,
                   db.func.count(Service.user_user_activities)
                   .label('total'))\
            .filter(Service.title.startswith(search_string))\
            .outerjoin(UserUserActivity)\
            .group_by(Service.id)\
            .order_by('total DESC')\
            .limit(7)\
            .all()

        return jsonify({
            'query': search_string,
            'suggestions': [
                {'value': s.title, 'data': s.id}
                for s, act in services
            ]
        })

    except NoResultFound:
        return jsonify({
            'query': search_string,
            'suggestions': []
        })


class SearchSpecialist(TemplateView):
    template_name = 'Search.html'

    def __init__(self):
        super(SearchSpecialist, self).__init__()
        self.service = None

    def get(self, service_id, *args, **kwargs):
        self.service = Service.query.get(service_id)

        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super(SearchSpecialist, self).get_context_data(**kwargs)
        context.update({'current_service': self.service})
        context.update({'specialists': self.get_specialists()})
        context.update({'similar_services': self.get_similar_services()})

        return context

    def get_specialists(self):
        """
        Return all specialists of selected service.
        If user allowed usage of his current location specialists would
        be sorted by proximity
        """

        if not current_user_location:
            return self.service.specialists.all()

        specialist_info = [
            {
                'specialist': s,
                'distance': get_distance(s.user.location.longitude,
                                         s.user.location.latitude,
                                         current_user_location['longitude'],
                                         current_user_location['latitude'])
            }
            for s in self.service.specialists.all()
        ]

        return [
            item['specialist']
            for item in sorted(specialist_info, key=lambda d: d['distance'])
        ]

    def get_similar_services(self):
        # db query which selects services which have the
        # same category as selected service and have at least one
        # Specialist entry.
        # Order by count of UserUserActivity entries.
        similar_services = db.session\
            .query(Service, db.func.count(Service.user_user_activities)
                   .label('total'))\
            .filter(Service.category == self.service.category,
                    Service.id != self.service.id)\
            .join(SpecialistService)\
            .group_by(Service.id)\
            .having(db.func.count(SpecialistService.specialist_id) > 0)\
            .outerjoin(UserUserActivity)\
            .order_by('total DESC')\
            .limit(3)\
            .all()

        return [s for s, count in similar_services]

app.add_url_rule(
    '/service/<int:service_id>',
    view_func=SearchSpecialist.as_view('search_specialist')
)


def get_distance(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6367 * c

    return km


@app.route('/set_current_location', methods=['POST'])
def set_current_location():
    """
    Func which receives current user location
    and sets it to global variable
    :return:
    """

    data = json.loads(request.data)
    global current_user_location
    current_user_location = data
    return jsonify({
        'status': 'ok'
    })
