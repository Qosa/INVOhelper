import os
from flask import Flask
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import secure_filename

app = Flask(__name__,static_url_path='/static')
Bootstrap(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app) 
lm = LoginManager(app)

from app.main import api, user, items, invent, comments, docs

for blueprint in [api, user, items, invent, comments, docs]:
    app.register_blueprint(blueprint)

from app import models
db.init_app(app)
