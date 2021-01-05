# -*- coding:utf-8 -*-
from app import db
from app.models import Item, Comment, ItemList
from flask import url_for, flash, redirect, request, abort
from . import comments
from .forms import CommentForm


@comments.route('/add/<int:occur_id>/', methods=['POST', ])
def add(occur_id):
    form = CommentForm()
    occurrence = ItemList.query.get_or_404(occur_id)
    lastId = Comment.query.order_by(Comment.id.desc()).first().id
    if form.validate_on_submit():
        the_comment = Comment(id=lastId+1,occur_id=occur_id, comment=form.comment.data)
        db.session.add(the_comment)
        db.session.commit()
        flash(u'Komentarz został opublikowany', 'success')
    return redirect(request.args.get('next') or url_for('items.occurrence_details', occur_id=occur_id))
