from functools import wraps
import jwt
from flask import abort, request, jsonify
from flask_login import current_user
from app import app
from app.models import User, TokenBlacklist


def invent_permissions_required(f):
    @wraps(f)
    def inv_decorated_function(*args, **kwargs):
        print(current_user.role)
        if current_user.role != 1:
            if current_user.role != 4:
                if request.view_args['inv_id'] not in current_user.stocktakings:
                    abort(403)
                if current_user.role == 3:
                    abort(403)
        return f(*args, **kwargs)
    return inv_decorated_function

def permissions_required(f):
    @wraps(f)
    def per_decorated_function(*args, **kwargs):
        if current_user.role == 3:
            abort(403)
        return f(*args, **kwargs)
    return per_decorated_function

def admin_required(f):
    @wraps(f)
    def adm_decorated_function(*args, **kwargs):
        if current_user.role != 1:
            abort(403)
        return f(*args, **kwargs)
    return adm_decorated_function

def token_required(f):
    @wraps(f)
    def tok_decorated_function(*args, **kwargs):

        token = None

        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']

        if not token:
            return jsonify({'message': 'nie przeslano tokenu!'})

        blacklist_check = TokenBlacklist.query.filter_by(token=token).first()  
        if blacklist_check != None:
            return jsonify({'message': 'token jest nieważny!'})

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'token jest nieprawidłowy'})

        return f(*args, **kwargs)
    return tok_decorated_function    
