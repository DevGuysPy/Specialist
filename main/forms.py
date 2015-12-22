from flask_wtf import Form
from wtforms import StringField, DateTimeField, SelectField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, optional
from models import Specialist, Customer, Service


class SearchForm(Form):
    query = StringField('query', validators=[DataRequired()])


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
    description = StringField('description', validators=[optional()])
    start = DateTimeField('start_rel', format='%Y-%d-%m %H:%M:%S', validators=[optional()])
    end = DateTimeField('end_rel', format='%Y-%d-%m %H:%M:%S', validators=[optional()])

    def validate(self):
        if not super(AddServiceActivityForm, self).validate():
            return False
        result = True
        if self.start.data > self.end.data:
            result = False

        return result
