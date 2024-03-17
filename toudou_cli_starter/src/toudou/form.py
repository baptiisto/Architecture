from flask_wtf import FlaskForm
from wtforms import StringField ,SubmitField,RadioField
from wtforms.validators import DataRequired , ValidationError
from wtforms.fields import DateField
from datetime import date , datetime
from toudou import FORMAT

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
                self.data = datetime.strptime(date_str, self.format[0]).date()
            except ValueError:
                self.data = None
                raise ValueError(self.gettext('Not a valid date value'))

def validerDate(form,champ):
    print(form.data['date'])
    if form.data['date'] is not None:
        if form.data['date'] <= date.today():
            raise ValidationError("La date d'achèvement doit être supérieure à la date d'aujourd'hui.")



class FormCreate(FlaskForm):
    nameTodo = StringField("Nom du Todo", validators=[DataRequired()])
    etat =RadioField("Etat",choices=[("True","Terminé"),("False","En Cours")],default='False')
    date = NullableDateField('Date de la Todo', validators=[validerDate],format=FORMAT)
    valider = SubmitField('Valider')

