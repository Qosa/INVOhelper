from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms import StringField, validators, TextAreaField, MultipleFileField, FileField, SubmitField

class AddItemForm(FlaskForm):
    name = StringField('Nazwa', validators=[validators.DataRequired(message=u"Proszę wypełnić to pole!"),
                                   validators.Length(1, 128, message=u"Długość od 1 do 128 znaków.")])
    index_nbr = StringField('Indeks')
    description = TextAreaField('Opis')
    submit = SubmitField(u"Zatwierdź")

class AddOccurrenceForm(FlaskForm):
    inv_number = StringField('Indeks')
    localization = StringField('Lokalizacja')
    img = FileField('Zdjecie')
    documents = FileField('Załącznik')    
    submit = SubmitField(u"Zatwierdź")
