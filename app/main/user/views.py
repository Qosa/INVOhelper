from . import user
from ..decorators import permissions_required, admin_required
from app import db
from app.models import User, Stocktaking
from flask import render_template, url_for, flash, redirect, request, abort, Markup
from flask_login import login_user, logout_user, login_required, current_user
from .forms import LoginForm, RegistrationForm, EditForm, AdminChangePasswordForm, ChangePasswordForm


@user.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        the_user = User.query.filter(User.login.ilike(form.login.data)).first()
        if the_user is not None and the_user.verify_password(form.password.data):
            login_user(the_user, form.remember_me.data)
            if the_user.role == 1:
                return redirect(url_for('user.user_admin'))
            elif the_user.role == 2:
                return redirect(url_for('user.user_commember'))    
            else:
                flash(u'%s - Logowanie zakończone sukcesem!' % the_user.login, 'success')
                return redirect(url_for('user.details'))
        flash(u'Niepoprawne dane logowania!', 'danger')
    return render_template("login.html", form=form)

@user.route('/logout/')
@login_required
def logout():
    logout_user()
    flash(u'Wylogowano pomyślnie!', 'info')
    return redirect(url_for('user.login'))

@user.route('/admin/')
@admin_required
def user_admin():
    return render_template("admin-panel.html")

@user.route('/commember/')
@permissions_required    
def user_commember():
    return render_template("commember-panel.html")

@user.route('/register/', methods=['GET', 'POST'])
@admin_required
def register():
    form = RegistrationForm()
    stocktakings_pending = Stocktaking.query.filter_by(finished=False)
    form.stocktakings.choices = [(stocktaking.id, 'Nr.'+str(stocktaking.id)) for stocktaking in stocktakings_pending]
    if form.validate_on_submit():
        the_user = User(login=form.login.data,
                        password=form.password.data,
                        role=form.accountType.data,
                        stocktakings=form.stocktakings.data)
        db.session.add(the_user)
        db.session.commit()
        flash('Dodano nowego użytkownika!','info')
        return redirect(url_for('user.user_list'))
    return render_template('user-register.html', form=form)

@user.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def user_edit(user_id):
    form_user = EditForm()
    form_password = AdminChangePasswordForm()
    the_user = User.query.get_or_404(user_id)
    stocktakings_pending = Stocktaking.query.filter_by(finished=False)
    form_user.stocktakings.choices = [(stocktaking.id, 'Nr.'+str(stocktaking.id)) for stocktaking in stocktakings_pending]
    if form_user.validate_on_submit():
        the_user.role = form_user.accountType.data
        the_user.login = form_user.login.data
        the_user.stocktakings = form_user.stocktakings.data
        db.session.add(the_user)
        db.session.commit()
        flash(Markup('Pomyślnie edytowano użytkownika! Powrót do listy: <a href="/user/list/">link</a>'),'info')
    if form_password.validate_on_submit():
        the_user.password = form_password.new_password.data
        db.session.add(the_user)
        db.session.commit()
        flash(Markup('Hasło zostało zmienione! Powrót do listy: <a href="/user/list/">link</a>'),'info')      
    form_user.accountType.process_data(the_user.role)
    form_user.login.data = the_user.login
    if form_user.stocktakings.data == None:
        pass
    form_user.stocktakings.data = [stocktaking for stocktaking in the_user.stocktakings]    
    return render_template('user-edit.html', form_user=form_user, form_password=form_password)

@user.route('/details/', methods=['GET', 'POST'])
@login_required
def details():
    form = ChangePasswordForm()
    if current_user.role == 1:
        role = 'Administrator'
    elif current_user.role == 2:
        role = 'Członek komisji'
    else:
        role = 'Skaner'        
    if form.validate_on_submit():
        current_user.password = form.new_password.data
        db.session.add(current_user)
        db.session.commit()
        flash(u'Hasło zostało zmienione!', 'info')
        return redirect(url_for('user.details'))
    return render_template('user-details.html', form=form, role=role)  

@user.route('/list/')
@admin_required
def user_list():
    users = User.query
    return render_template('user-list.html', users=users)

@user.route('/<int:user_id>/delete')
@admin_required
def user_delete(user_id):
    if user_id == 1: #zabezpieczenie konta administratora
        abort(403) 
    the_user = User.query.get_or_404(user_id)
    db.session.delete(the_user)
    db.session.commit()
    flash(u'Pomyślnie usunięto użytkownika!', 'success')
    return redirect(url_for('user.user_list'))  

