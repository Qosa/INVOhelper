from . import api
from collections.abc import Iterable
from flask import render_template, request, redirect, url_for, flash, jsonify
from app import db
from app.models import Stocktaking, ItemList, Unknown, Item, Schedule, Evidenced

@api.route('/item/get/<int:inv_id>/<inv_number>', methods=['GET'])
def api_get_item(inv_id,inv_number):
    try:
        evidenced = Evidenced.query.filter_by(inv_id=inv_id)
        occurrence = ItemList.query.filter_by(inv_number=inv_number).first()
        item = Item.query.get_or_404(occurrence.item_id)
        items_evidenced = []
        for ev in evidenced:
            items_evidenced.append(ev.item_id)
        if occurrence.id in items_evidenced:
            inv_response = 3
        else:
            inv_response = 2  
        data = {'name':item.name, 'inv_response':inv_response}
    except:
        try:
            unknown = Unknown.query.filter_by(inv_number=inv_number,inv_id=inv_id).first()
            inv_response = 1    
            data = {'name':'unknown', 'inv_response':inv_response}
        except:
            inv_response = 0    
            data = {'name':'unknown', 'inv_response':inv_response}    
    return jsonify({'data': data})

@api.route('/item/post/add', methods=['GET', 'POST'])
def api_add_item():
    if request.method == 'POST':
        postData = request.get_json()
        inv_number = postData["item_inv_number"]
        inv_id = postData["inv_id"]
        occurrence = ItemList.query.filter_by(inv_number=inv_number).first()    
        lastId = Evidenced.query.order_by(Evidenced.id.desc()).first().id
        evidenced = Evidenced(lastId+1,inv_id,occurrence.id)
        db.session.add(evidenced)
        db.session.commit()
        data = {'inv_id':inv_id,'inv_item_number':inv_number,'comment':'jakies gowno','inv_response':1}
    else:
        print('Nic z tego!!')
        data = {'inv_id':1,'inv_item_number':'1000010000006','comment':'jakies gowno','inv_response':0}

    return jsonify({'data':data})
