import os

basedir = os.path.abspath(os.path.dirname(__file__))
#DATABASE = os.path.join(basedir, 'app.db')

MAX_CONTENT_LENGTH = 1024 * 1024

UPLOAD_EXTENSIONS = ['.pdf', '.PDF']

UPLOAD_PATH = 'uploads'

TEMPLATES_AUTO_RELOAD = True

JSON_AS_ASCII = False

#SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost:5432/invohelper'

SQLALCHEMY_DATABASE_URI = 'postgres://rmuwodwxizvomv:68d9a2ed7cb3bdf90df6e084fb709a4468597c1a875b7b91917c4f2560758fdb@ec2-52-31-94-195.eu-west-1.compute.amazonaws.com:5432/d5tl0po5fk7fpd'

SECRET_KEY = 'you-will-never-guess'

FLASKY_ADMIN = 'root@gmail.com'

SQLALCHEMY_TRACK_MODIFICATIONS = False
