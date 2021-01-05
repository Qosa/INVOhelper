from flask_wtf import FlaskForm
from wtforms import StringField, validators, FormField, TextAreaField, FileField, SubmitField, FieldList, TextField, BooleanField
from wtforms.fields.html5 import DateField

class AddItemForm(FlaskForm):
    name = StringField('Nazwa', validators=[validators.DataRequired(message=u"Proszę wypełnić to pole!"),
                                   validators.Length(1, 128, message=u"Długość od 1 do 128 znaków.")])
    inv_number = StringField('Numer inwentarzowy')
    description = TextAreaField('Opis')
    localization = StringField('Lokalizacja')
    image = FileField('zdjecie')
    attachment = FileField('Załącznik')
    submit = SubmitField(u"Zatwierdź")

class Creator(FlaskForm):
    commissioner_name = StringField(render_kw={"class":"form-control","placeholder": "Imię"})
    commissioner_surname = StringField(render_kw={"class":"form-control","placeholder": "Nazwisko"})
    flist_members = FieldList(TextField())
    flist_schedule = FieldList(TextField())
    localization = StringField(render_kw={"class":"form-control","placeholder": "Lokalizacja"})
    mpk_number = StringField(render_kw={"class":"form-control","placeholder": "Numer MPK"})
    submit = SubmitField('Submit') 

class Sample2(FlaskForm):
    commissioner_name = StringField(render_kw={"class":"form-control","placeholder": "Imię"})
    commissioner_surname = StringField(render_kw={"class":"form-control","placeholder": "Nazwisko"})
    localization = StringField(render_kw={"class":"form-control","placeholder": "Lokalizacja"})
    mpk_number = StringField(render_kw={"class":"form-control","placeholder": "Numer MPK"})
    submit = SubmitField('Submit') 

class AddTask(FlaskForm):
    date_start = DateField('Data startu', format='%Y-%m-%d',validators=[validators.DataRequired(message=u"Proszę wypełnić to pole!")],render_kw={"class":"form-control"})
    onetimer = BooleanField('Wydarzenie jednorazowe')
    date_exp_end = DateField('Data końca', format='%Y-%m-%d',validators=[validators.DataRequired(message=u"Proszę wypełnić to pole!")],render_kw={"class":"form-control"})
    task = StringField('Zadanie',validators=[validators.DataRequired(message=u"Proszę wypełnić to pole!"),
                                   validators.Length(1, 128, message=u"Długość od 1 do 128 znaków.")],render_kw={"class":"form-control","placeholder": "Zadanie"})
    submit = SubmitField('Submit') 

