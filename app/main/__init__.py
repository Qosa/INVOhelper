# -*- coding:utf-8 -*-
from app import lm
from app.models import User

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

from .user import user
from .items import items
from .invent import invent
from .comments import comments
from .api import api