# -*- encoding: utf-8 -*-
import json
from datetime import date

from sqlalchemy import desc, func
from flask import (render_template, url_for, jsonify, redirect, request,
                   session, abort)
from flask_views.base import TemplateView
from flask_views.edit import FormView
from sqlalchemy.orm.exc import NoResultFound
from flask.ext.login import login_user, current_user, login_required

from app import app, db, api_manager

from models import (Specialist, Service, UserUserActivity, Company, User,
                    SpecialistService, ServiceCategory, Location,
                    get_experience_types)
from utils import (generate_confirmation_token, send_email,
                   send_user_verification_email,
                   account_not_found, page_not_found)
from forms import (AddServiceActivityForm, RegistrationForm,
                   SpecialistForm, LoginForm)

from geopy.distance import great_circle


current_user_location = None

api_manager.create_api(Specialist, exclude_columns=[
    'experience', 'user.password', 'user.phone_number'])


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
        self.stats['total_activities'] = UserUserActivity.query.count()
        self.stats['specialists'] = len(Specialist.query.all())
        self.stats['specialists_online'] = "1"
        # Coming soon
        #  self.stats['online'] = User.query.filter()
        self.stats['users'] = User.query.count()
        self.stats['services'] = Service.query.count()
        self.stats['categories'] = ServiceCategory.query.count()
        self.stats['new_users'] = User.query \
            .filter(func.date(User.registration_time) == date.today()).count()

        if self.stats['new_users']:
            self.stats['new_users_in_percents'] = 0

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
                    password=form.password.data)

        db.session.add(user)
        db.session.flush()

        send_user_verification_email(user.id)

        session['signing_up_user_id'] = user.id

        if 'login' in request.args:
            login_user(user)

        return jsonify({
            'status': 'ok',
            'user_id': user.id
        })

    return jsonify({
        'status': 'error',
        'errors': form.errors
    })


@app.route('/account/add_services', methods=['POST'])
@login_required
def add_services_to_specialist():
    services = []
    for service_id in json.loads(request.data).get('selected_service_ids', []):
        service = Service.query.filter_by(id=service_id).first()
        if not service:
            return jsonify({
                'status': 'error',
            })

        if service not in current_user.specialist.services:
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
                street=form.location.street.data,
                building=form.location.building.data,
                latitude=form.location.latitude.data,
                longitude=form.location.longitude.data)

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
    decorators = [login_required]

    def __init__(self):
        super(AccountSpecialist, self).__init__()
        self.user = None

    def dispatch_request(self, *args, **kwargs):
        self.user = current_user
        self.set_template_name()
        return super(AccountSpecialist, self).dispatch_request(*args, **kwargs)

    def get(self, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(AccountSpecialist, self).get_context_data()
        context.update({'user': current_user})
        context.update({'spec_form': SpecialistForm()})
        context.update({
            'latest_activities': self.get_latest_u_u_services_activities()
        })

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
        for service in self.user.specialist.services:
            rel = UserUserActivity.query\
                .filter_by(service=service,
                           from_user=self.user,
                           confirmed=True)\
                .order_by(desc(UserUserActivity.start)).first()
            latest_activities[service.title] = rel

        return latest_activities

    def set_template_name(self):
        if self.user.specialist:
            self.template_name = 'user/AccountSettingsSpecialist.html'
        else:
            self.template_name = 'user/CreateSpecialist.html'


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

        return context

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
        return context


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

    q = (Service.title.startswith(search_string), )
    if 'category' in request.args:
        try:
            category = ServiceCategory.query.filter(
                ServiceCategory.id == request.args['category']).one()
        except NoResultFound:
            return abort(404)

        q += (Service.category == category, )

    try:
        # db query which selects services which start with search string.
        # Order by count of UserUserActivity entries.
        services = db.session\
            .query(Service,
                   db.func.count(Service.user_user_activities)
                   .label('total'))\
            .filter(*q)\
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


@app.route('/autocomplete/categories')
def category_autocomplete():
    if 'query' not in request.args:
        return page_not_found()

    query = request.args['query']

    search_string = query.strip()

    try:
        # db query which selects services which start with search string.
        # Order by count of UserUserActivity entries.
        categories = db.session\
            .query(ServiceCategory,
                   db.func.count(ServiceCategory.services)
                   .label('total'))\
            .filter(ServiceCategory.title.startswith(search_string))\
            .outerjoin(Service)\
            .group_by(ServiceCategory.id)\
            .order_by('total DESC')\
            .limit(7)\
            .all()

        return jsonify({
            'query': search_string,
            'suggestions': [
                {'value': s.title, 'data': s.id}
                for s, act in categories
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
        self.page = None
        self.specialist_count = None

    def get(self, service_id, *args, **kwargs):
        self.service = Service.query.get(service_id)
        try:
            self.page = int(request.args.get('page', 1))
            if self.page < 1:
                return redirect(
                    url_for(
                        'search_specialist',
                        service_id=self.service.id) + '?page=1')
        except ValueError:
            return redirect(
                url_for(
                    'search_specialist',
                    service_id=self.service.id) + '?page=1')

        if request.is_xhr:
            spec = self.get_specialists()
            template = render_template(
                "SearchSpecialistCards.html",
                specialists=spec,
                specialists_count=self.specialist_count,
                current_page=self.page,
                current_service=self.service)
            return json.dumps({
                'template': template,
                'specialists_count': self.specialist_count,
                'current_page': self.page
            })
        else:
            context = self.get_context_data()

            return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(SearchSpecialist, self).get_context_data(**kwargs)
        context.update({'current_service': self.service})
        context.update({'similar_services': self.get_similar_services()})
        context.update({'experience_types': json.dumps(get_experience_types())})

        return context

    def get_specialists_sorted_by_dist(
            self,
            specialists=None,
            radius=None,
            lat=None,
            lng=None):
        """
        Sort specialists which have current service entry by proximity
        to given coordinates.
        Return list of Specialist objects.
        """

        if specialists:
            extra_filter = 'AND Specialist.id IN {}'\
                .format(tuple(s.id for s in specialists))
        else:
            extra_filter = None

        spec_infos = db.engine.execute(
            'SELECT Specialist.id, Location.latitude, Location.longitude '
            'FROM specialist_service '
            'INNER JOIN Specialist ON '
            'Specialist.id = specialist_service.specialist_id '
            'INNER JOIN users ON users.id = Specialist.user_id '
            'INNER JOIN Location ON Location.id = users.location_id '
            'WHERE specialist_service.service_id = {} {}'
            .format(self.service.id, extra_filter or ''))

        distances = \
            [
                (
                    s[0],
                    great_circle((lat, lng), (s[1], s[2])).meters
                )
                for s in spec_infos
                if not radius or
                great_circle((lat, lng), (s[1], s[2])).meters < radius
            ]

        sorted_dist = sorted(distances, key=lambda dist: dist[1])

        ids = [s[0] for s in sorted_dist]

        if specialists:
            specialists = specialists.filter(Specialist.id.in_(ids))
        else:
            specialists = self.service.specialists

        return sorted(specialists, key=lambda spec: ids.index(spec.id))

    def get_specialists(self):
        """
        Return specialists of selected service sliced according to current page.
        If there are request args specialists would be sorted by given params.
        Else specialists would be sorted by proximity to current user location.
        """

        args_list = ['lat_lng', 'radius', 'exp_from', 'exp_to',
                     'success_from', 'success_to', 'city_loc']

        # number of specialists on current page
        from_user_number = (self.page - 1) * 12
        to_user_number = self.page * 12

        specialists = self.service.specialists

        set_default_sorting = False
        if any(arg in request.args for arg in args_list):
            if 'exp_from' in request.args or 'exp_to' in request.args:
                try:
                    specialists = specialists.filter(Specialist.experience.in_(
                        [str(i) for i in
                         range(
                             int(request.args.get('exp_from', 0)),
                             int(request.args.get('exp_to', 11)) + 1)]))
                except ValueError:
                    pass

            if 'city_loc' in request.args:
                try:
                    city, country = request.args['city_loc'].split(',')
                except ValueError:
                    city = country = None

                if city and country:
                    specialists = specialists\
                        .join(User)\
                        .join(Location)\
                        .filter(Location.city == city,
                                Location.country == country)

            # Sorting by success jobs, orders count,
            # average price will be added later.
            # We haven't anything which is related to this
        else:
            set_default_sorting = True

        if 'sort_by' in request.args:
            # sort by
            # 1 - first the most experienced
            # 2 - first the least experienced
            # 5 - first the nearest
            # 6 - first the farthest

            sorting = request.args['sort_by']

            if sorting == '1':
                specialists = \
                    sorted(specialists,
                           key=lambda s: int(s.experience.code),
                           reverse=True)
            elif sorting == '2':
                specialists = \
                    sorted(specialists,
                           key=lambda s: int(s.experience.code))
            elif (sorting == '5' or sorting == '6') and \
                    'lat_lng' in request.args and \
                    'city_loc' not in request.args:
                try:
                    lat, lng = request.args['lat_lng'].split(',')
                    lat = float(lat)
                    lng = float(lng)
                except ValueError:
                    lat = lng = None

                if lat and lng:
                    if 'radius' in request.args:
                        try:
                            radius = int(request.args['radius']) * 1000
                        except ValueError:
                            radius = None
                    else:
                        radius = None

                    specialists = self.get_specialists_sorted_by_dist(
                        radius=radius,
                        lat=lat,
                        lng=lng,
                        specialists=specialists)

                if sorting == '6':
                    specialists = list(reversed(specialists))
        elif set_default_sorting and session.get('current_user_location'):
            current_location = \
                session['current_user_location']['geometry']['location']
            lng = current_location['lng']
            lat = current_location['lat']

            specialists = self.get_specialists_sorted_by_dist(
                lat=lat, lng=lng)

        if not isinstance(specialists, list):
            specialists = specialists.all()

        self.specialist_count = len(specialists)

        return specialists[from_user_number:to_user_number]

    def get_similar_services(self):
        """
        db query which selects services which have the
        same category as selected service and have at least one
        Specialist entry.
        Order by count of UserUserActivity entries.
        """
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


@app.route('/set_current_location', methods=['POST'])
def set_current_location():
    """
    Func which receives current user location
    and sets it to global variable
    :return:
    """

    data = json.loads(request.data)
    session['current_user_location'] = data
    return jsonify({
        'status': 'ok'
    })


@app.route('/add_order', methods=['POST'])
@login_required
def create_order():
    data = json.loads(request.data)
    service_id = data.get('service_id')
    user_id = data.get('user_id')
    if not (user_id and service_id):
        return abort(400)

    try:
        from_user = User.query.filter_by(id=int(user_id)).one()
        service = Service.query.filter_by(id=int(service_id)).one()
    except (ValueError, NoResultFound):
        return abort(400)
    location = data.get('location')

    if location and location.get('country') and location.get('lng') and \
            location.get('lat'):
        location = Location(
            country=location['country'],
            state=location.get('administrative_area_level_1'),
            city=location.get('locality'),
            street=location.get('route'),
            building=location.get('street_number'),
            longitude=location.get('lng'),
            latitude=location.get('lat'))
        db.session.add(location)
        db.session.flush()
    else:
        location = None

    order = UserUserActivity(
        from_user=from_user,
        to_user=current_user,
        service=service,
        description=data.get('description'),
        start=data.get('start') or None,
        end=data.get('end') or None,
        location=location,
        timing_type=data.get('timing_type', '0'))

    db.session.add(order)
    db.session.flush()

    return jsonify({
        'status': 'ok',
        'redirect_url': url_for('order', id=order.id)
    })

