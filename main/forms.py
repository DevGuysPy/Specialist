from sqlalchemy import exists
from flask_wtf import Form
from wtforms_alchemy import model_form_factory
from wtforms import StringField, DateTimeField, ValidationError, IntegerField
from wtforms.validators import DataRequired

from models import ServiceActivity, Specialist, Customer, Service, db


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
        model = ServiceActivity
        only = ['description', 'end']

    specialist_id = IntegerField('Specialist',
                                 validators=[
                                     DataRequired(),
                                     validate_id_for(Specialist)
                                 ])
    customer_id = IntegerField('Customer',
                               validators=[
                                   DataRequired(),
                                   validate_id_for(Customer)
                               ])
    service_id = IntegerField('Service',
                              validators=[
                                  DataRequired(),
                                  validate_id_for(Service)
                              ])
    start = DateTimeField('Start',
                          validators=[
                              DataRequired(),
                              validate_start_end
                          ])
