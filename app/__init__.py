import os
from flask import Flask

app = Flask(__name__)

app.config.from_object('config')

from app.main import admin, user, items

for blueprint in [user, items, admin]:
    app.register_blueprint(blueprint)
