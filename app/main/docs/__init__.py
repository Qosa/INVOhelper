from flask import Blueprint

docs = Blueprint('docs', __name__, url_prefix='/docs', template_folder='templates')

from . import views