from app import db
from app.models import User
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, SelectMultipleField, widgets
from wtforms import ValidationError
from wtforms.validators import Email, Length, DataRequired, EqualTo, Required

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class LoginForm(FlaskForm):
    login = StringField('login',
                        validators=[DataRequired(message=u"Proszę uzupełnić to pole!"), Length(5, 64)],render_kw={"class":"form-control","placeholder": "Login"})
    password = PasswordField(u'Hasło', validators=[DataRequired(message=u"Proszę uzupełnić to pole!"), Length(8, 32)],render_kw={"class":"form-control","placeholder": "Hasło"})
    token = StringField('Token',render_kw={"class":"form-control","placeholder": "Token"})
    remember_me = BooleanField(u"Zapamiętaj mnie", default=True)
    submit = SubmitField(u'Zaloguj się',render_kw={"class":"btn btn-success"})


class RegistrationForm(FlaskForm):
    accountType = SelectField(u'Typ konta', choices = [(2, 'Komisja'), (3, 'Skaner'), (4, 'JST')], validators = [Required()],render_kw={"class":"form-control"})
    login_reg = StringField(u'Nazwa użytkownika', validators=[DataRequired(message=u"Proszę uzupełnić to pole!"), Length(1, 64)], render_kw={"class":"form-control","placeholder": "Podaj login","autocomplete":"chrome-off"})
    password_reg = PasswordField(u'Hasło',
                             validators=[DataRequired(message=u"Proszę uzupełnić to pole!"), EqualTo('password2', message=u'Hasła muszą być zgodne!'),
                                         Length(6, 32)],render_kw={"class":"form-control","placeholder": "Podaj hasło","autocomplete":"new-password"})
    password2 = PasswordField(u'Potwierdź hasło', validators=[DataRequired(message=u"Proszę uzupełnić to pole!")],render_kw={"class":"form-control","placeholder": "Powtórz hasło"})
    stocktakings = MultiCheckboxField('label', coerce=int)
    submit = SubmitField(u'Zarejestruj',render_kw={"class":"btn btn-success"})

class EditForm(FlaskForm):
    accountType = SelectField(u'Typ konta', choices = [(2, 'Komisja'), (3, 'Skaner'), (4, 'JST')], validators = [Required()],render_kw={"class":"form-control"})
    login = StringField(u'Nazwa użytkownika', validators=[DataRequired(message=u"Proszę uzupełnić to pole!"), Length(1, 64)],render_kw={"class":"form-control","placeholder": "Login"})
    stocktakings = MultiCheckboxField('label', coerce=int)
    submit = SubmitField(u'Edytuj',render_kw={"class":"btn btn-success"})

class AdminChangePasswordForm(FlaskForm):
    new_password = PasswordField(u'Nowe hasło', validators=[DataRequired(message=u"Proszę uzupełnić to pole!"),
                                                     EqualTo('confirm_password', message=u'Hasła muszą być zgodne'),
                                                     Length(6, 32)], render_kw={"class":"form-control","placeholder": "Nowe hasło"})
    confirm_password = PasswordField(u'Potwierdź nowe hasło', validators=[DataRequired(message=u"Proszę uzupełnić to pole!")], render_kw={"class":"form-control","placeholder": "Powtórz hasło"})
    submit = SubmitField(u"Zapisz hasło",render_kw={"class":"btn btn-success"})

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(u'Stare hasło', render_kw={"class":"form-control","placeholder": "Stare hasło"})
    new_password = PasswordField(u'Nowe hasło', validators=[DataRequired(message=u"Proszę uzupełnić to pole!"),
                                                     EqualTo('confirm_password', message=u'Hasła muszą być zgodne'),
                                                     Length(6, 32)], render_kw={"class":"form-control","placeholder": "Nowe hasło"})
    confirm_password = PasswordField(u'Potwierdź nowe hasło', validators=[DataRequired(message=u"Proszę uzupełnić to pole!")], render_kw={"class":"form-control","placeholder": "Powtórz hasło"})
    submit = SubmitField(u"Zapisz hasło",render_kw={"class":"btn btn-success"})

    def validate_old_password(self, filed):
        from flask_login import current_user
        if not current_user.verify_password(filed.data):
            raise ValidationError(u'Stare hasło jest nieprawidłowe!')
