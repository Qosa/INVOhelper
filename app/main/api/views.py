from . import api
from ..decorators import token_required
from collections.abc import Iterable
import datetime
from flask import render_template, request, redirect, url_for, flash, jsonify, make_response
import jwt
from werkzeug.security import check_password_hash
from app import app, db
from app.models import Stocktaking, ItemList, Unknown, Item, Schedule, Evidenced, Comment, User, TokenBlacklist

@api.route('/login', methods=['GET', 'POST'])  
def api_login_user(): 
 
    auth = request.authorization   

    if not auth or not auth.username or not auth.password:  
        return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})    

    user = User.query.filter_by(login=auth.username).first()   
     
    if check_password_hash(user.password_hash, auth.password):  
        token = jwt.encode({'public_id': user.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])  
        return jsonify({'token' : token.decode('UTF-8')}) 

    return make_response('could not verify',  401, {'WWW.Authentication': 'Basic realm: "login required"'})

@api.route('/logout', methods=['GET', 'POST'])  
@token_required
def api_logout_user(): 
    token = request.headers['x-access-tokens']
    db.session.add(TokenBlacklist(token=token))
    db.session.commit()
    data = { 'response':'token blacklisted!' }
    return jsonify({'data': data})

@api.route('/item/get/<int:inv_id>/<inv_number>', methods=['GET'])
@token_required
def api_get_item(inv_id,inv_number):
    try:
        evidenced = Evidenced.query.filter_by(inv_id=inv_id)
        occurrence = ItemList.query.filter_by(inv_number=inv_number).first()
        item = Item.query.get_or_404(occurrence.item_id)
        items_evidenced = []
        for ev in evidenced:
            items_evidenced.append(ev.item_id)
        if occurrence.id in items_evidenced:
            inv_response = 2
        else:
            inv_response = 1  
        data = {'name':item.name, 'inv_response':inv_response}
    except:
        try:
            unknown = Unknown.query.filter_by(inv_number=inv_number,inv_id=inv_id).first()
            print(unknown.inv_number)
            inv_response = 2    
            data = {'name':'NIEZNANY', 'inv_response':inv_response}
        except:
            inv_response = 0    
            data = {'name':'NIEZNANY', 'inv_response':inv_response}    
    return jsonify({'data': data})

@api.route('/item/post/add', methods=['GET', 'POST'])
@token_required
def api_add_item():
    if request.method == 'POST':
        postData = request.get_json()
        inv_number = postData["item_inv_number"]
        inv_id = postData["inv_id"]
        comment = postData["comment"]
        occurrence = ItemList.query.filter_by(inv_number=inv_number).first()    
        lastIdEvidenced = Evidenced.query.order_by(Evidenced.id.desc()).first().id
        lastIdComment = Comment.query.order_by(Comment.id.desc()).first().id
        evidenced = Evidenced(lastIdEvidenced+1,inv_id,occurrence.id)
        if comment == "":
            pass
        else:
            commentAdd = Comment(lastIdComment+1,occurrence.id,comment)
            db.session.add(commentAdd)
        db.session.add(evidenced)
        db.session.commit()
        data = {'inv_id':inv_id,'inv_item_number':inv_number,'comment':comment,'inv_response':1}
    else:
        print('Nic z tego!!')
        data = {'inv_id':inv_id,'inv_item_number':inv_number,'comment':comment,'inv_response':0}

    return jsonify({'data':data})

@api.route('/item/post/add_unknown', methods=['GET', 'POST'])
@token_required
def api_add_unknown():
    if request.method == 'POST':
        postData = request.get_json()
        inv_number = postData["inv_number"]
        inv_id = postData["inv_id"]
        localization = postData["localization"]
        description = postData["description"]
        lastIdUnknown = Unknown.query.order_by(Unknown.id.desc()).first().id
        unknown = Unknown(lastIdUnknown+1,inv_id,inv_number,localization,description)
        db.session.add(unknown)
        db.session.commit()        
        data = {'inv_id':inv_id,'inv_number':inv_number,'description':description,'localization':localization, 'inv_response':1}
    else:
        data = {'inv_id':inv_id,'inv_number':inv_number,'description':description,'localization':localization, 'inv_response':0}   

    return jsonify({'data':data})     

