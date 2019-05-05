
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, SelectMultipleField

class ProjectionForm(FlaskForm):
    relation = SelectField('Seleccione una relacion ', choices=[])
    fragment_count = StringField('Numero de fragmentos ')
    selected_attributes = SelectMultipleField(label='Seleccione atributos ', choices=[])
