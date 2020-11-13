from flask_wtf import FlaskForm
from wtforms import StringField, validators, TextAreaField, FileField, SubmitField, FieldList, TextField

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