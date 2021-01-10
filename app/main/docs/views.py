import os
from . import docs
from ..decorators import permissions_required, admin_required
from app import app,db
from app.models import ItemList, Item, Stocktaking
from flask import render_template, url_for, flash, redirect, request, abort, Markup
from flask_login import login_user, logout_user, login_required, current_user
from .forms import LoginForm, RegistrationForm, EditForm, AdminChangePasswordForm, ChangePasswordForm

def make_tree(path):
    tree = dict(name=path, children=[])
    try: lst = os.listdir(path)
    except OSError:
        pass #ignore errors
    else:
        for name in lst:
            fn = os.path.join(path, name)
            if os.path.isdir(fn):
                tree['children'].append(make_tree(fn))
            else:
                tree['children'].append(dict(name=fn))
    return tree

@docs.route('/attachments/list')
@permissions_required
def docs_attach_list():
    attachments = []
    tree = make_tree(app.config['UPLOADED_DOCS_DEST'])
    for elem in tree['children']:
        attachment = {}
        inv_number = elem['name'].split('docs/',1)[1]
        occur = ItemList.query.filter_by(inv_number=inv_number.replace('-','/')).first() 
        item = Item.query.get_or_404(occur.item_id)
        attachment['folder_name'] = inv_number
        attachment['occur_id'] = occur.id
        attachment['item_name'] = item.name 
        attachment['file_name'] = elem['children'][0]['name'].split(inv_number+'\\',1)[1]
        attachments.append(attachment)
    return render_template("docs-attach-list.html",attachments=attachments)

@docs.route('/attachments/occurrence/<inv_number>/<filename>')
@permissions_required
def docs_occur_attach(inv_number,filename):
    return render_template("docs-occur-attach.html", inv_number=inv_number, filename=filename)

@docs.route('/invent/list')
@permissions_required
def docs_inv_list():
    if current_user.role == 1 or current_user.role == 4:
        stocktakings_pending = Stocktaking.query.filter_by(finished=False).order_by(Stocktaking.id)
        stocktakings_ended = Stocktaking.query.filter_by(finished=True).order_by(Stocktaking.id)
    else:    
        for stocktaking in current_user.stocktakings:
            stocktakings_pending = Stocktaking.query.filter_by(id=stocktaking,finished=False).order_by(Stocktaking.id)
            stocktakings_ended = Stocktaking.query.filter_by(id=stocktaking,finished=True).order_by(Stocktaking.id)
    return render_template('docs-inv-list.html', stocktakings_pending=stocktakings_pending, stocktakings_ended=stocktakings_ended) 

@docs.route('/invent/<int:inv_id>/attachments')
@permissions_required
def docs_inv_attach(inv_id):
    finished = Stocktaking.query.get_or_404(inv_id).finished
    print(finished)
    return render_template("docs-inv-attach.html",inv_id=inv_id,finished=finished)       
