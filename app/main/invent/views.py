from flask import render_template, request, redirect, url_for, flash
from . import invent
from . import forms
from app import db
from app.models import Stocktaking, ItemList, Unknown, Item

@invent.route('/creator', methods=['GET', 'POST'] )
def creator():
    form = forms.Creator(request.form)
    if request.method == 'POST' and form.validate():
        print(form.flist_members.data)   
        flash(u'Dodano pozycję!', 'success')
        return redirect(url_for('items.index'))
    return render_template('inv-creator.html', form=form)   

@invent.route('/creator/test', methods=['GET', 'POST'] )
def test():    
    form = forms.Sample2(request.form)
    if request.method == 'POST' and form.validate():
        print('dziala')
    return render_template('test.html', form=form)

@invent.route('/list', methods=['GET', 'POST'] )
def inv_list():       
    stocktakings_pending = Stocktaking.query.filter_by(finished=False)
    stocktakings_ended = Stocktaking.query.filter_by(finished=True)
    return render_template('inv-list.html', stocktakings_pending=stocktakings_pending, stocktakings_ended=stocktakings_ended)

@invent.route('/<int:inv_id>/details', methods=['GET', 'POST'] )
def inv_details(inv_id):         
    stocktaking = Stocktaking.query.get_or_404(inv_id)
    items_evidenced = []
    for i in stocktaking.evidenced:
        items_evidenced.append(ItemList.query.get_or_404(i))
    items_nonevidenced = []
    for i in ItemList.query:
        items_nonevidenced.append(i.id)
    print(items_nonevidenced)    
    items_nonevidenced = list(set(items_nonevidenced) - set(items_evidenced))
    print(list(set(items_nonevidenced) - set(items_evidenced)))    
    items_unknown = Unknown.query.filter_by(inv_id=inv_id)
    return render_template('inv-details.html', stocktaking=stocktaking, items_evidenced=items_evidenced, items_nonevidenced=items_evidenced, items_unknown=items_unknown)

@invent.route('/<int:inv_id>/document', methods=['GET', 'POST'] )
def inv_document(inv_id):   
    stocktaking = Stocktaking.query.get_or_404(inv_id)
    items = []
    for i in stocktaking.evidenced:
        items.append(ItemList.query.get_or_404(i))
    return render_template('pdf-template.html', stocktaking=stocktaking, items=items)