from flask import render_template, request, redirect, url_for, flash
from . import invent
from . import forms
from app import db
import datetime
from calendar import monthrange
from app.models import Stocktaking, ItemList, Unknown, Item, Schedule

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

def previous_month_link(year, month):
    if month > 1:
        month -=1
    else:
        year -=1
        month = 12    
    return (
        ""
        "?y={}&m={}".format(year, month)
    )

def next_month_link(year, month):
    if month < 12:
        month +=1
    else:
        year +=1
        month = 1    
    return (
        ""
        "?y={}&m={}".format(year, month)
    )

@invent.route('/<int:inv_id>/schedule', methods=['GET', 'POST'])    
def inv_schedule(inv_id):
    tasks = Schedule.query.filter_by(inv_id=inv_id)
    tasks_pending = Schedule.query.filter_by(inv_id=inv_id,finished=False)
    tasks_ended = Schedule.query.filter_by(inv_id=inv_id,finished=True)
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    months = ['Styczeń', 'Luty', 'Marzec', 'Kwiecień', 'Maj', 'Czerwiec', 'Lipiec', 'Sierpień', 'Wrzesień', 'Październik', 'Listopad', 'Grudzień']
    current_month_name = months[month-1]
    if request.method == 'GET' and request.args.get("y") is not None and request.args.get("m") is not None:
        year = int(request.args.get("y"))
        month = int(request.args.get("m"))
        current_month_name = months[month-1]
    if month > 1:    
        prev_month_data = monthrange(year,month-1)
    else:
        prev_month_data = monthrange(year-1,12)    
    month_data = monthrange(year,month)
    print(tasks[0].date_start.month)
    return render_template('inv-schedule.html', 
                            inv_id=inv_id,
                            tasks=tasks,
                            month=month,
                            current_month_name = current_month_name,
                            tasks_pending=tasks_pending,
                            tasks_ended=tasks_ended,
                            month_data=month_data, 
                            prev_month_data=prev_month_data, 
                            previous_month_link=previous_month_link(year,month),
                            next_month_link=next_month_link(year,month)
                            )

@invent.route('/<int:inv_id>/schedule/finish/<int:task_id>/', methods=['GET', 'POST'])
def inv_task_finish(inv_id,task_id):
    task = Schedule.query.filter_by(inv_id=inv_id,id=task_id).first()
    task.finished = True
    db.session.commit()
    flash(u'Pomyślnie edytowano zadanie!','success')
    return redirect(url_for('invent.inv_schedule', inv_id=inv_id))

@invent.route('/<int:inv_id>/schedule/retrieve/<int:task_id>/', methods=['GET', 'POST'])
def inv_task_retrieve(inv_id,task_id):
    task = Schedule.query.filter_by(inv_id=inv_id,id=task_id).first()
    task.finished = False
    db.session.commit()
    flash(u'Pomyślnie edytowano zadanie!','success')
    return redirect(url_for('invent.inv_schedule', inv_id=inv_id))  

@invent.route('/<int:inv_id>/schedule/addtask/', methods=['GET', 'POST'])
def inv_task_add(inv_id): 
    form = forms.AddTask(request.form)
    lastId = Schedule.query.order_by(Schedule.id.desc()).first().id
    print(lastId)
    if request.method == 'POST' and form.validate():
        task = Schedule(lastId+1,inv_id,form.date_start.data, form.date_end.data,
                    form.task.data)
        db.session.add(task)
        db.session.commit()
        flash(u'Dodano zadanie!', 'success')
        return redirect(url_for('invent.inv_schedule'))
    return render_template('inv-add-task.html', form=form)    

@invent.route('/<int:inv_id>/schedule/edit/<int:task_id>/', methods=['GET', 'POST'])
def inv_task_edit(inv_id,task_id):      
    task = Schedule.query.filter_by(inv_id=inv_id,id=task_id).first()
    form = forms.AddTask(request.form)
    if form.validate_on_submit():
        task.date_start = form.date_start.data
        task.date_end = form.date_end.data
        task.task = form.task.data
        db.session.add(task)
        db.session.commit()
        flash(u'Pomyślnie edytowano zadanie!','success')
        return redirect(url_for('invent.schedule'))
    form.date_start.data = task.date_start
    form.date_end.data = task.date_end
    form.task.data = task.task
    return render_template("inv-add-task.html", form=form, task=task, title=u"Edytuj zadanie") 

@invent.route('/<int:inv_id>/schedule/delete/<int:task_id>/')
def inv_task_delete(inv_id,task_id):
    task = Schedule.query.filter_by(inv_id=inv_id,id=task_id).first()
    db.session.delete(task)
    db.session.commit()
    flash(u'Pomyślnie usunięto zadanie!', 'danger')
    return redirect(url_for('invent.inv_schedule', inv_id=inv_id))      