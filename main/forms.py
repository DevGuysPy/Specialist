from flask_wtf import Form
from wtforms_alchemy import model_form_factory
from wtforms import StringField, DateTimeField, ValidationError, IntegerField
from wtforms.validators import DataRequired
from models import ServiceActivity, Specialist, Customer, Service


BaseModelForm = model_form_factory(Form)


class SearchForm(Form):
    query = StringField('query', validators=[DataRequired()])


def start_end_validation(form, field):
    if form.end.data and field.data > form.end.data:
        raise ValidationError(
            'Start of activity must be earlier than end of activity')


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