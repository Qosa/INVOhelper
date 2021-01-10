from app import db
from datetime import datetime, timedelta
from sqlalchemy.dialects import postgresql
from flask_login import UserMixin
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import onetimepass

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String())
    login = db.Column(db.String(64), unique=True)
    password_hash = db.deferred(db.Column(db.String(128)))
    role = db.Column(db.Integer())
    stocktakings = db.Column(db.ARRAY(db.Integer()))
    created = db.Column(db.DateTime(), default=datetime.utcnow)
    otp_secret = db.Column(db.String(16))

    @property
    def password(self):
        raise AttributeError('password is not readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.public_id = str(uuid.uuid4())
        self.otp_secret = base64.b32encode(os.urandom(10)).decode('utf-8')

    def get_totp_uri(self):
        return 'otpauth://totp/invohelper:{0}?secret={1}&issuer=invohelper' \
            .format(self.login, self.otp_secret)    

    def verify_totp(self, token):
        return onetimepass.valid_totp(token, self.otp_secret)            

    def is_scanner(self):
        return self.scanner

class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    index_nbr = db.Column(db.String())
    description = db.Column(db.String())

    def __init__(self, name, index_nbr, description):
        self.name = name
        self.index_nbr = index_nbr
        self.description = description

    def __repr__(self):
        return f"<Item {self.name}>"

    def count_occurrences(self):
        return ItemList.query.filter_by(item_id=self.id).count()    

class ItemList(db.Model):
    __tablename__ = 'items_list'

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer(), db.ForeignKey('items.id'))
    inv_number = db.Column(db.String())
    add_date = db.Column(db.DateTime(),default=datetime.now())
    localization = db.Column(db.String())
    img = db.Column(db.String())
    documents = db.Column(db.String())

    comments = db.relationship('Comment', backref='item',
                               lazy='dynamic',
                               cascade='all, delete-orphan')

    def __init__(self, item_id, inv_number, localization, img, documents):
        self.item_id = item_id
        self.inv_number = inv_number
        self.add_date = datetime.now()
        self.localization = localization
        self.img = img
        self.documents = documents 

    def get_item_name(self, item_id):
        item = Item.query.get_or_404(item_id)
        return item.name      

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    #user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('items_list.id'))
    comment = db.Column(db.String(1024))
    create_timestamp = db.Column(db.DateTime, default=datetime.now())
    edit_timestamp = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, id, occur_id, comment):
        #self.user = user
        self.id = id
        self.item_id = occur_id
        self.comment = comment
        self.create_timestamp = datetime.now()
        self.edit_timestamp = datetime.now()
        self.deleted = 0

class Schedule(db.Model):
    __tablename__ = 'schedule'
    id = db.Column(db.Integer, primary_key=True)
    inv_id = db.Column(db.Integer, db.ForeignKey('stocktaking.id'))   
    date_start = db.Column(db.DateTime)
    date_end = db.Column(db.DateTime)
    date_exp_end = db.Column(db.DateTime)
    task = db.Column(db.String())
    finished = db.Column(db.Boolean())

    def __init__(self, id, inv_id, date_start, date_exp_end, task):
        self.id = id
        self.inv_id = inv_id
        self.date_start = date_start
        self.date_exp_end = date_exp_end
        self.task = task
        self.finished = False

class Stocktaking(db.Model):
    __tablename__ = 'stocktaking'
    id = db.Column(db.Integer, primary_key=True)
    localization = db.Column(db.String())
    mpk_number = db.Column(db.Integer())
    commissioner = db.Column(db.String())
    com_members = db.Column(postgresql.ARRAY(db.String(), dimensions=1))
    finished = db.Column(db.Boolean(),default=False)
    date_start = db.Column(db.DateTime(),default=datetime.now())
    date_stop = db.Column(db.DateTime())

    def __init__(self, id, localization, mpk_number, commissioner, com_members):
        self.id = id
        self.localization = localization
        self.mpk_number = mpk_number
        self.commissioner = commissioner
        self.com_members = com_members

class Generator(db.Model):
    __tablename__ = 'generator'
    id = db.Column(db.Integer, primary_key=True)      
    generated_value = db.Column(db.String())

    def __init__(self, generated_value):
        self.generated_value = generated_value

class Unknown(db.Model):
    __tablename__ = 'unknown'
    id = db.Column(db.Integer, primary_key=True)   
    inv_id = db.Column(db.Integer, db.ForeignKey('stocktaking.id'))    
    inv_number = db.Column(db.String())
    localization = db.Column(db.String())
    add_date = db.Column(db.DateTime(),default=datetime.now())
    description = db.Column(db.String())

    def __init__(self, id, inv_id, inv_number, localization, description):
        self.id = id
        self.inv_id = inv_id
        self.inv_number = inv_number
        self.localization = localization
        self.description = description

class Evidenced(db.Model):
    __tablename__ = 'evidenced'
    id = db.Column(db.Integer, primary_key=True)      
    inv_id = db.Column(db.Integer, db.ForeignKey('stocktaking.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('items_list.id'))
    add_date = db.Column(db.DateTime(),default=datetime.now())

    def __init__(self, id, inv_id, item_id):
        self.id = id
        self.inv_id = inv_id
        self.item_id = item_id      

class TokenBlacklist(db.Model):
    __tablename__ = 'token_blacklist'
    id = db.Column(db.Integer, primary_key=True)      
    token = db.Column(db.String())

    def __init__(self, token):
        self.token = token           