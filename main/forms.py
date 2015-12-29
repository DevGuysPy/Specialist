from flask_wtf import Form

from wtforms import StringField, DateTimeField, ValidationError, IntegerField, validators, TextAreaField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, optional, Email
from models import Specialist, Customer, Service


class SearchForm(Form):
    query = StringField('query', validators=[DataRequired()])


def start_end_validation(form, field):
    if form.end.data and field.data > form.end.data:
        raise ValidationError(
            'Start of activity must be earlier than end of activity')


class AddServiceActivityForm(Form):
    specialist = QuerySelectField(
        query_factory=Specialist.query.all,
        get_pk=lambda a: a.id,
        get_label=lambda a: a.name)
    customer = QuerySelectField(
        query_factory=Customer.query.all,
        get_pk=lambda a: a.id,
        get_label=lambda a: a.name)
    service = QuerySelectField(
        query_factory=Service.query.all,
        get_pk=lambda a: a.id,
        get_label=lambda a: a.title)
    description = StringField('Description', validators=[optional()])
    start = DateTimeField('Start', format='%Y-%d-%m %H:%M:%S',
                          validators=[start_end_validation])
    end = DateTimeField('End', format='%Y-%d-%m %H:%M:%S',
                        validators=[optional()])


def validation_on_existed_email(form, field):
    email_to_be = Specialist.query.filter_by(email=form.email.data).all()
    if email_to_be:
        raise ValidationError(
            'This email already exists')

def validation_on_existed_phone(form, field):
    phone_to_be = Specialist.query.filter_by(phone=form.phone.data).all()
    if phone_to_be:
        raise ValidationError(
            'This phone already exists')

class SpecialistForm(Form):
    name = StringField('name',
                       [validators.Length(min=4, max=50), DataRequired()])
    email = StringField('email',
                        [validators.Length(min=6, max=35),
                         DataRequired(), Email(),
                         validation_on_existed_email])
    phone = StringField('phone',
                        [validators.Length(min=5, max=12),
                         DataRequired(), validation_on_existed_phone])
    experience = IntegerField('experience',
                              [validators.NumberRange(min=3, max=70),
                               DataRequired()])
    description = TextAreaField('description',
                                [validators.Length(max=750), DataRequired()])

