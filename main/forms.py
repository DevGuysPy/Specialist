from flask_wtf import Form

from wtforms import StringField, DateTimeField, ValidationError, IntegerField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, optional, Email, Length, NumberRange, EqualTo
from wtforms_alchemy import model_form_factory

from models import ServiceActivity, Specialist, AbstractUser, Customer


BaseModelForm = model_form_factory(Form)



class SearchForm(Form):
    query = StringField('query', validators=[DataRequired()])


def start_end_validation(form, field):
    if form.end.data and field.data > form.end.data:
        raise ValidationError(
            'Start of activity must be earlier than end of activity')


class UniqueValidator(object):

    def __init__(self, model, field, message=None):
        self.model = model
        self.field = field
        if not message:
            message = u'Already exists'
        self.message = message

    def __call__(self, form, field):
        existing = self.model.query.filter(self.field == field.data).first()
        if existing:
            raise ValidationError(self.message)


# class LoginForm(Form):
#     username = StringField(
#         'username',
#         validators=[
#             DataRequired()
#         ]
#     )
#     password = PasswordField(
#         'password',
#         validators=[
#             DataRequired()
#         ]
#     )
#     confirm_password = PasswordField(
#         'repeat password',
#         validators=[
#             DataRequired(),
#             EqualTo('password', message='Passwords must match')
#         ]
#     )

class CustomerForm(Form):
    class Meta:
        model = AbstractUser

    first_name = StringField(
        'first_name',
        validators=[
            DataRequired(),
            Length(max=128)
        ]
    )
    last_name = StringField(
        'last_name',
        validators=[
            DataRequired(),
            Length(max=128)
        ]
    )
    username = StringField(
        'username',
        validators=[
            DataRequired(),
            Length(max=128),
            UniqueValidator(Specialist, Specialist.username)
        ]
    )
    password = PasswordField(
        'password',
        validators=[
            DataRequired()
        ]
    )
    confirm_password = PasswordField(
        'repeat password',
        validators=[
            DataRequired(),
            EqualTo('password', message='Passwords must match')
        ]
    )
    email = StringField(
        'email',
        validators=[
            DataRequired(),
            Length(max=255),
            Email(),
            UniqueValidator(Specialist, Specialist.email)
        ]
    )
    phone = StringField(
        'phone',
        validators=[
            DataRequired(),
            Length(min=5, max=12),
            UniqueValidator(Specialist, Specialist.phone)
        ]
    )


class SpecialistForm(Form):
    class Meta:
        model = AbstractUser

    first_name = StringField(
        'first_name',
        validators=[
            DataRequired(),
            Length(max=128)
        ]
    )
    last_name = StringField(
        'last_name',
        validators=[
            DataRequired(),
            Length(max=128)
        ]
    )
    username = StringField(
        'username',
        validators=[
            DataRequired(),
            Length(max=128),
            UniqueValidator(Specialist, Specialist.username)
        ]
    )
    password = PasswordField(
        'password',
        validators=[
            DataRequired()
        ]
    )
    confirm_password = PasswordField(
        'repeat password',
        validators=[
            DataRequired(),
            EqualTo('password', message='Passwords must match')
        ]
    )
    email = StringField(
        'email',
        validators=[
            DataRequired(),
            Length(max=255),
            Email(),
            UniqueValidator(Specialist, Specialist.email)
        ]
    )
    phone = StringField(
        'phone',
        validators=[
            DataRequired(),
            Length(min=5, max=12),
            UniqueValidator(Specialist, Specialist.phone)]
    )
    experience = IntegerField(
        'experience',
        validators=[
            DataRequired(),
            NumberRange(max=100)
        ]
    )
    description = TextAreaField(
        'description',
        validators=[
            Length(max=750),
            optional()]
    )


def id_exist(form, field):
    model = eval(field.label.text)
    if model.query.filter(model.id == field.data).count() == 0:
        raise ValidationError('{} does not exist'.format(field.label.text))


class AddServiceActivityForm(BaseModelForm):
    class Meta:
        model = ServiceActivity
        only = ['description', 'end']

    specialist_id = IntegerField('Specialist',
                                 validators=[DataRequired(), id_exist])
    customer_id = IntegerField('Customer',
                               validators=[DataRequired(), id_exist])
    service_id = IntegerField('Service',
                              validators=[DataRequired(), id_exist])
    start = DateTimeField('Start',
                          validators=[DataRequired(), start_end_validation])

