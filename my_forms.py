
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField

class SelectRelationForm(FlaskForm):
    def __init__(self, relations):
        """ relations: list<tuple>
        """
        self.relations = SelectField('Relacion', relations) 