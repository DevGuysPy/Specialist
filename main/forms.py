from sqlalchemy import exists, or_
from flask_wtf import Form, RecaptchaField

from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms_alchemy import model_form_factory, Unique, ModelFormField

from wtforms import (StringField, DateTimeField, ValidationError,
                     PasswordField, IntegerField, DateField, RadioField)


from wtforms.validators import DataRequired, Length, Email, EqualTo, \
                                 StopValidation
from wtforms_components import PhoneNumberField

from models import (UserUserActivity, db, Service, User,
                    Specialist, Location, Company)


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
        form.service.query = specialist.services
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
    birth_date = DateField("Birth Date", validators=[DataRequired()])
    recaptcha = RecaptchaField()


class LocationForm(BaseModelForm):
    class Meta:
        model = Location
        validators = [DataRequired()]


class LocationForm(BaseModelForm):
    class Meta:
        model = Location


class SpecialistForm(BaseModelForm):
    class Meta:
        model = Specialist
        only = ['experience', 'description']

    def __init__(self, user, *args, **kwargs):
        super(SpecialistForm, self).__init__(*args, **kwargs)
        self.user = user


    phone = PhoneNumberField('Phone',
                        validators=[
                            DataRequired(
                                message=u'You should set the correct '
                                        u'phone number')])

    service_id = IntegerField('Service',
                              validators=[
                                  DataRequired(message='You must select '
                                                       'at least one '
                                                       'service you offer')
                              ])

    location = ModelFormField(LocationForm)


class ServiceForm(BaseModelForm):
    class Meta:
        model = Service


class CompanyForm(BaseModelForm):
    class Meta:
        model = Company


class LoginForm(Form):
    email = StringField('Email',
                        validators=[DataRequired(),
                                    Email()])
    password = PasswordField('Password',
                             validators=[
                                 DataRequired()])


class ChangePasswordForm(Form):

    def __init__(self, user, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.user = user

    def check_current_password(self, field):
        if self.user.password != field.data:
            raise ValidationError(u'Invalid Password')

    def check_new_password(self, field):
        if self.user.password == field.data:
            raise ValidationError(
                u'This password is identical to yours current')

    current_password = PasswordField('Password',
                                     validators=[
                                        DataRequired(),
                                        check_current_password])
    new_password = PasswordField('new_password',
                                 validators=[
                                    DataRequired(),
                                    EqualTo('new_password_again',
                                            message='Passwords must match'),
                                    check_new_password,
                                    Length(min=8, max=64)])
    new_password_again = PasswordField('new_password_again',
                                       validators=[
                                            DataRequired(),
                                            Length(min=8, max=64),
                                            EqualTo('new_password',
                                                    message='Passwords must match')])


class SetPhoneForm(BaseModelForm):
    class Meta:
        model = User
        only = ['main_phone', 'extra_phone']

    def __init__(self, user, *args, **kwargs):
        super(SetPhoneForm, self).__init__(*args, **kwargs)
        self.user = user

    # unique validator checking main and extra phone on existing
    def check_on_existing(self, field):
        existing = self.user.query.filter(or_(self.user.main_phone == field.data, self.user.extra_phone == field.data))\
            .first()
        if existing:
            raise ValidationError(u'Already exists')

    number = PhoneNumberField('Set_phone',
                              validators=[
                                DataRequired(
                                    message=u'Enter your phone '
                                            u'number following to '
                                            u'your country code'),
                                check_on_existing]
                             )
    type = RadioField(choices=[('0', 'Main'), ('1', 'Extra')])


class EditUserProfileForm(BaseModelForm):
    class Meta:
        model = User
        only = ['first_name', 'last_name', 'email', 'birth_date']

    def __init__(self, user, *args, **kwargs):
        super(EditUserProfileForm, self).__init__(*args, **kwargs)
        self.user = user

    def check_equality_to_current_email(self, field):
        if self.user.email == field.data:
            raise StopValidation()

    email = StringField('Email', validators=[DataRequired(),
                                             Email(),
                                             check_equality_to_current_email,
                                             Unique(User.email),])
    first_name = StringField('FirstName', validators=[DataRequired(message=u'Required')])
    last_name = StringField('LastName', validators=[DataRequired(message=u'Required')])
    birth_date = DateField("Birth Date", validators=[DataRequired()])


class EmailForm(Form):
    recovery_email = StringField('Email', validators=[DataRequired(),
                                                      Email()])


class ResetPasswordForm(Form):

    new_password_recover = PasswordField('Password',
                                         validators=[
                                             DataRequired(),
                                             EqualTo('new_password_again_recover',
                                                     message='Passwords must match'),
                                             Length(min=8, max=64)])
    new_password_again_recover = PasswordField('PasswordAgain',
                                               validators=[
                                                   DataRequired(),
                                                   Length(min=8, max=64),
                                                   EqualTo('new_password_recover',
                                                           message='Passwords must match')])