import os
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from flask_uploads import UploadSet, IMAGES, configure_uploads

app = Flask(__name__,static_url_path='/static')
Bootstrap(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app) 
photos = UploadSet('photos', IMAGES)
docs = UploadSet('docs', ['pdf'])
configure_uploads(app, (photos, docs))
from app.main import admin, api, user, items, invent, comments
for blueprint in [admin, api, user, items, invent, comments]:
    app.register_blueprint(blueprint)

from app import models
db.init_app(app)
