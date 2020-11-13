import os

basedir = os.path.abspath(os.path.dirname(__file__))
#DATABASE = os.path.join(basedir, 'app.db')

MAX_CONTENT_LENGTH = 1024 * 1024

UPLOAD_EXTENSIONS = ['.pdf', '.PDF']

UPLOAD_PATH = 'uploads'

TEMPLATES_AUTO_RELOAD = True

SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost:5432/invohelper'

SECRET_KEY = 'you-will-never-guess'

FLASKY_ADMIN = 'root@gmail.com'

SQLALCHEMY_TRACK_MODIFICATIONS = False
