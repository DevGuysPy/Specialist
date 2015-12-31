from flask_wtf import Form

from wtforms import StringField, DateTimeField, ValidationError, IntegerField, TextAreaField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, optional, Email, Length, NumberRange
from wtforms_components import Unique
from models import Specialist, Customer, Service, AbstractUser


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

class SpecialistForm(Form):
    name = StringField('name',
                       validators=[
                            DataRequired(),
                            Length(max=128),])
    email = StringField('email',
                        validators=[
                            DataRequired(),
                            Length(max=255),
                            Email(),
                            UniqueValidator(Specialist, Specialist.email)])
    phone = StringField('phone',
                        validators=[
                            DataRequired(),
                            Length(min=5, max=12),
                            UniqueValidator(Specialist, Specialist.phone)])
    experience = IntegerField('experience',
                              validators=[
                                DataRequired(),
                                NumberRange(min=1, max=70)])
    description = TextAreaField('description',
                                validators=[
                                    DataRequired(),
                                    Length(max=750),
                                    optional()])

