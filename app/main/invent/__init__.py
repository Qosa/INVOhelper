from flask import Blueprint

invent = Blueprint('invent', __name__, url_prefix='/invent', template_folder='templates')

from . import views