from sqlalchemy import exists
from flask_wtf import Form
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms_alchemy import model_form_factory, Unique
from wtforms import StringField, DateTimeField, ValidationError, PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms_components import PhoneNumberField
from flask.ext.login import current_user

from models import UserUserActivity, db, Service, User, \
    Specialist


BaseModelForm = model_form_factory(Form)


class SearchForm(Form):
    query = StringField('query', validators=[DataRequired()])


def validate_start_end(form, field):
    if form.end.data and field.data > form.end.data:
        raise ValidationError(
            'Start of activity must be earlier than end of activity')


def validate_id_for(model):
    def validate_id(form, field):
        if not db.session.query(
                exists().where(model.id == field.data)).scalar():
            raise ValidationError(
                '{} with id {} does not exist'.format(
                    model.__name__, field.data))
    return validate_id


class AddServiceActivityForm(BaseModelForm):
    class Meta:
        model = UserUserActivity
        only = ['description', 'end']

    service = QuerySelectField(
        query_factory=None,
        get_pk=lambda a: a.id,
        get_label=lambda a: a.title)
    start = DateTimeField('Start',
                          validators=[
                              DataRequired(),
                              validate_start_end
                          ])

    @classmethod
    def get_form(cls, specialist):
        form = cls()
        form.service.query = specialist.services.all()
        return form


def validate_full_name(form, field):
    if len(field.data.split(' ')) <= 1:
        raise ValidationError(
            'Please enter a valid full name. Example: John Folstrom')


class RegistrationForm(BaseModelForm):
    class Meta:
        model = User
        only = ['email', 'password']

    full_name = StringField('Full Name',
                            validators=[
                                DataRequired(),
                                validate_full_name])
    email = StringField('Email', validators=[DataRequired(),
                                             Email(),
                                             Unique(User.email)])
    password = StringField('Password',
                           validators=[
                               DataRequired(),
                               Length(min=4, max=64)])


class SpecialistForm(BaseModelForm):
    class Meta:
        model = Specialist
        only = ['experience', 'description']

    phone = PhoneNumberField('Phone', country_code='UA',
                             validators=[DataRequired()])


class ServiceForm(BaseModelForm):
    class Meta:
        model = Service


class LoginForm(Form):
    email = StringField('Email',
                        validators=[DataRequired(),
                                    Email()])
    password = PasswordField('Password',
                             validators=[
                                 DataRequired()])


def check_password_on_equality(form, field):
    if current_user.password == field.data:
        raise ValidationError(u'This password is identical to yours one')


def check_password(form, field):
    if current_user.password != field.data:
        raise ValidationError(u'Invalid password')


class SettingsForm(Form):

    current_password = PasswordField('Password',
                                     validators=[
                                        DataRequired(),
                                        check_password])
    new_password = PasswordField('new_password',
                                 validators=[
                                    DataRequired(),
                                    EqualTo('new_password_again',
                                            message='Passwords must match'),
                                    check_password_on_equality,
                                    Length(min=4, max=64)])
    new_password_again = PasswordField('new_password_again',
                                       validators=[
                                            DataRequired(),
                                            Length(min=4, max=64),
                                            EqualTo('new_password',
                                                    message='Passwords must match')])