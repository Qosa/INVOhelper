from flask import Blueprint

comments = Blueprint('comments', __name__, url_prefix='/comments', template_folder='templates')

from . import views
