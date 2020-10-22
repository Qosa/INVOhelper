from flask import render_template
from . import items

@items.route('/')
def index():
    return render_template('items-list.html')

@items.route('/details')
def details():
    return render_template('item-details.html')   