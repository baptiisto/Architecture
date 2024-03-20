import csv
import io
import uuid
from flask_wtf import FlaskForm
from wtforms import StringField ,SubmitField,RadioField , validators
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired , ValidationError
from wtforms.fields import DateField ,SelectField
from datetime import date , datetime
from toudou import FORMAT


def validerDate(form,champ):
    if form.data['date'] is not None:
        if form.data['date'] <= date.today():
            raise ValidationError("La date d'achèvement doit être supérieure à la date d'aujourd'hui.")

def valider_csv(self, field):
    csv_content = field.data.read().decode('utf-8')
    csv_reader = csv.reader(io.StringIO(csv_content))
    headers = next(csv_reader)

    expected_headers = ["task", "complete", "due"]
    if headers != expected_headers:
        raise ValidationError('Les en-têtes du fichier CSV ne sont pas valides.')
class FormCreate(FlaskForm):
    nameTodo = StringField("Nom du Todo", validators=[DataRequired()])
    etat =RadioField("Etat",choices=[("True","Terminé"),("False","En Cours")],default='False')
    date = DateField('Date de la Todo', validators=[validerDate,validators.Optional()],format=FORMAT)
    valider = SubmitField('Valider')

class FormDelete(FlaskForm):
    select_field = SelectField('Choisir une Todo à enlever', validators=[DataRequired()], coerce=uuid.UUID)
    valider = SubmitField('Valider')

class FormUpdate(FlaskForm):
    select_field = SelectField('Choisir une Todo à modifier', validators=[DataRequired()], coerce=uuid.UUID)
    nameTodo = StringField("Nom du Todo", default=None)
    etat =RadioField("Etat",choices=[("True","Terminé"),("False","En Cours")],default='False')
    date = DateField('Date de la Todo', validators=[validerDate,validators.Optional()],format=FORMAT)
    valider = SubmitField('Valider')

class FormImport(FlaskForm):
    csv_file = FileField('Choisir un fichier CSV',validators=[DataRequired(), FileAllowed(['csv']),valider_csv])
    valider = SubmitField('Valider')