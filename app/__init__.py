import os
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__,static_url_path='/static')
Bootstrap(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app) 

from app.main import admin, api, user, items, invent, comments
for blueprint in [admin, api, user, items, invent, comments]:
    app.register_blueprint(blueprint)

from app import models
db.init_app(app)
