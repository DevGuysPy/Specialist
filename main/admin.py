from flask.ext.login import current_user
from flask_admin.contrib.sqla import ModelView
from flask import abort

from app import db, admin
from models import User, Specialist, Service, ServiceCategory, UserUserActivity, ACTIVITY_STATUS_TYPES


class AdminView(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated and current_user.is_admin:
            return True
        return abort(404)


class UserAdmin(AdminView):
    column_exclude_list = ('password', 'bg_photo', 'profile_photo', 'registration_time')
    column_searchable_list = ['first_name', 'last_name', 'email', 'location.country', 'location.city']
    column_filters = ['first_name', 'last_name', 'location']


class SpecialistAdmin(AdminView):
    column_searchable_list = 'user.first_name', 'user.last_name', 'org.name'
    column_sortable_list = (('user', 'user.first_name'), ('org', 'org.name'), 'experience')
    column_labels = dict(org='Company')
    column_exclude_list = 'description'


class ActivityAdmin(AdminView):
    column_display_pk = True
    column_exclude_list = ('start', 'end', 'description', 'specialist_rating', 'customer_rating')
    column_filters = ['to_user.first_name',
                      'to_user.last_name',
                      'service.title',
                      'service.category.title',
                      'start', 'id']

    column_labels = dict(from_user='Specialist', to_user='Customer')
    column_sortable_list = (('service', 'service.title'),
                            ('from_user', 'from_user.first_name'),
                            ('to_user', 'to_user.first_name'),
                            'created_time', 'id', 'status')

    column_choices = {
        'status': [
            ACTIVITY_STATUS_TYPES[0],
        ]
    }


class ServiceAdmin(AdminView):
    # column_sortable_list = 'category', 'category.title', 'title'
    column_filters = ['category.title', 'title']
    column_searchable_list = ('category.title', 'title')

admin.add_view(UserAdmin(User, db.session))
admin.add_view(SpecialistAdmin(Specialist, db.session))
admin.add_view(ActivityAdmin(UserUserActivity, db.session))
admin.add_view(ServiceAdmin(Service, db.session))
admin.add_view(ModelView(ServiceCategory, db.session))

