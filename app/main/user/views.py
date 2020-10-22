from flask import render_template
from . import user

@user.route('/login')
def index():
    return render_template('login.html')