from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms import StringField, validators, TextAreaField, MultipleFileField, FileField, SubmitField

class AddItemForm(FlaskForm):
    name = StringField('Nazwa', validators=[validators.DataRequired(message=u"Proszę wypełnić to pole!"),
                                   validators.Length(1, 128, message=u"Długość od 1 do 128 znaków.")],render_kw={"class":"form-control","placeholder": "Nazwa"})
    index_nbr = StringField('Indeks',render_kw={"class":"form-control","placeholder": "Numer inwentarzowy"})
    description = TextAreaField('Opis',render_kw={"class":"form-control","placeholder": "Opis"})
    submit = SubmitField(u"Zatwierdź",render_kw={"class":"btn btn-success"})

class AddOccurrenceForm(FlaskForm):
    inv_number = StringField('Indeks',render_kw={"class":"form-control","placeholder": "Nr. inwentarzowy"})
    localization = StringField('Lokalizacja',render_kw={"class":"form-control","placeholder": "Lokalizacja"})
    img = FileField('Zdjecie')
    documents = FileField('Załącznik')    
    submit = SubmitField(u"Zatwierdź",render_kw={"class":"btn btn-success"})
