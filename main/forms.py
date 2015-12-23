from flask_wtf import Form
from wtforms import StringField, DateTimeField, ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, optional
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
