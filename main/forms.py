from flask_wtf import Form
from wtforms_alchemy import model_form_factory
from wtforms import StringField, DateTimeField, ValidationError, IntegerField
from wtforms.validators import DataRequired
from models import ServiceActivity, Specialist, Customer, Service


BaseModelForm = model_form_factory(Form)


class SearchForm(Form):
    query = StringField('query', validators=[DataRequired()])


def validate_start_end(form, field):
    if form.end.data and field.data > form.end.data:
        raise ValidationError(
            'Start of activity must be earlier than end of activity')


def validate_id_for(model):
    def validate_id(form, field):
        if model.query.filter(model.id == field.data).count() == 0:
            raise ValidationError('{} does not exist'.format(field.label.text))
    return validate_id


class AddServiceActivityForm(BaseModelForm):
    class Meta:
        model = ServiceActivity
        only = ['description', 'end']

    specialist_id = IntegerField('Specialist',
                                 validators=[DataRequired(), validate_id_for(Specialist)])
    customer_id = IntegerField('Customer',
                               validators=[DataRequired(), validate_id_for(Customer)])
    service_id = IntegerField('Service',
                              validators=[DataRequired(), validate_id_for(Service)])
    start = DateTimeField('Start',
                          validators=[DataRequired(), validate_start_end])
