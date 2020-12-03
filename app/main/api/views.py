from . import api
from collections.abc import Iterable
from flask import render_template, request, redirect, url_for, flash, jsonify
from app import db
from app.models import Stocktaking, ItemList, Unknown, Item, Schedule

@api.route('/item/<int:inv_id>/<inv_number>', methods=['GET'])
def api_get_item(inv_id,inv_number):
    stocktaking = Stocktaking.query.get_or_404(inv_id)
    occurrence = ItemList.query.filter_by(inv_number=inv_number).first()
    item = Item.query.get_or_404(occurrence.item_id)
    try:
        print(occurrence.id)
        print(stocktaking.evidenced)
        if occurrence.id in stocktaking.evidenced:
            inv_response = 2
        else:
            inv_response = 1  
    except:
        inv_response = 0    
    data = {'name':item.name, 'inv_response':inv_response}
    return jsonify({'data': data})

