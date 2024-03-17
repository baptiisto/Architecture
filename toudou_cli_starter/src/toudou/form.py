from flask_wtf import FlaskForm
from wtforms import StringField ,SubmitField,RadioField
from wtforms.validators import DataRequired , ValidationError
from wtforms.fields import DateField
from datetime import date

class NullableDateField(DateField):
    """Native WTForms DateField throws error for empty dates.
    Let's fix this so that we could have DateField nullable."""
    def process_formdata(self, valuelist):
        if valuelist:
            date_str = ' '.join(valuelist).strip()
            if date_str == '':
                self.data = None
                return
            try:
                self.data = datetime.datetime.strptime(date_str, self.format).date()
            except ValueError:
                self.data = None
                raise ValueError(self.gettext('Not a valid date value'))

def validerDate(form,champ):
    if champ.data is not None:
        if champ.data <= date.today():
            raise ValidationError("La date d'achèvement doit être supérieure à la date d'aujourd'hui.")
    else:
        print("Le champ de date est vide.")


class MyForm(FlaskForm):
    nameTodo = StringField("Nom du Todo", validators=[DataRequired()])
    etat =RadioField("Etat",choices=[("True","Terminé"),("False","En Cours")],default='False')
    date = NullableDateField('Date de la Todo', validators=[validerDate],default=None)
    valider = SubmitField('Valider')

