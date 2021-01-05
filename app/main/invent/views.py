from collections.abc import Iterable
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import invent
from . import forms
from ..decorators import invent_permissions_required, permissions_required, admin_required
from app import db
import datetime
from calendar import monthrange
from app.models import Stocktaking, ItemList, Unknown, Item, Schedule, Evidenced

@invent.route('/creator', methods=['GET', 'POST'] )
@admin_required
def creator():
    
    lastIdSchedule = Schedule.query.order_by(Schedule.id.desc()).first().id
    lastIdStocktaking = Stocktaking.query.order_by(Stocktaking.id.desc()).first().id
    if request.method == 'POST':

        members = []
        for i in range(len(request.form.getlist('memberName'))):
            members.append(request.form.getlist('memberName')[i]+" "+ request.form.getlist('memberSurname')[i])
        stocktaking = Stocktaking(lastIdStocktaking+1,request.form.get('invLocalization'),request.form.get('invMpk'),members[0],members[1:])    
        db.session.add(stocktaking)
        db.session.commit()
        for i in range(len(request.form.getlist('eventStartDate'))):
            task = Schedule(lastIdSchedule+i+1,stocktaking.id,request.form.getlist('eventStartDate')[i],request.form.getlist('eventEndDate')[i],request.form.getlist('eventTask')[i])
            db.session.add(task)
        db.session.commit()   
        flash(u'Dodano nową inwentaryzację!','success')
        return redirect(url_for('invent.inv_list'))
    
    return render_template('inv-creator.html')   

@invent.route('/list', methods=['GET', 'POST'] )
@permissions_required
def inv_list():       
    if current_user.role == 1:
        stocktakings_pending = Stocktaking.query.filter_by(finished=False)
        stocktakings_ended = Stocktaking.query.filter_by(finished=True)
    else:    
        for stocktaking in current_user.stocktakings:
            stocktakings_pending = Stocktaking.query.filter_by(id=stocktaking,finished=False)
            stocktakings_ended = Stocktaking.query.filter_by(id=stocktaking,finished=True)
    return render_template('inv-list.html', stocktakings_pending=stocktakings_pending, stocktakings_ended=stocktakings_ended)

class EvidencedItemView:
    def __init__(self, id, occur_id, inv_number, localization, add_date):
        self.id = id
        self.occur_id = occur_id
        self.inv_number = inv_number
        self.localization = localization
        self.add_date = add_date

@invent.route('/<int:inv_id>/details', methods=['GET', 'POST'] )
@invent_permissions_required
def inv_details(inv_id):     
    print(request.view_args['inv_id'])    
    stocktaking = Stocktaking.query.get_or_404(inv_id)
    evidenced = Evidenced.query.filter_by(inv_id=inv_id)
    items_evidenced = []
    item_ids_evidenced = []
    items_nonevidenced = []
    for evid in evidenced:
        occur = ItemList.query.get_or_404(evid.item_id)
        items_evidenced.append(EvidencedItemView(evid.id,evid.item_id,occur.inv_number,occur.localization,evid.add_date))
    if stocktaking.finished == True:
        items = ItemList.query
        print("zakonczona")
        try:
            for item in items_evidenced:
                item_ids_evidenced.append(item.id)
            for item in items:
                if item.id in item_ids_evidenced:
                    pass
                else:
                    items_nonevidenced.append(item)
        except:
            pass        
    print(items_evidenced)
    print(items_nonevidenced)       
    items_unknown = Unknown.query.filter_by(inv_id=inv_id)
    return render_template('inv-details.html', stocktaking=stocktaking, items_evidenced=items_evidenced, items_nonevidenced=items_nonevidenced, items_unknown=items_unknown)

@invent.route('/<int:inv_id>/details/invresponse', methods=['GET', 'POST'])
@invent_permissions_required
def inv_response(inv_id):
    inv_number = request.args.get('data')
    inv_response = 0
    print(inv_number)
    if inv_number:
        try:
            item = ItemList.query.filter_by(inv_number=inv_number).first()
            evidenced = Evidenced.query.filter_by(item_id=item.id).first()
            if evidenced != None:
                inv_response = 2
            else:
                inv_response = 1  
        except:
            unknown = Unknown.query.filter_by(inv_number=inv_number,inv_id=inv_id).first()
            if unknown != None:
                inv_response = 2
            else:        
                inv_response = 0     
    return render_template('inv-response.html', inv_response=inv_response, inv_id=inv_id, inv_number=inv_number)            

@invent.route('/<int:inv_id>/evidenced/add', methods=['GET', 'POST'])
@invent_permissions_required
def inv_evidenced_add(inv_id):
    inv_number = request.form.get('inv_number')
    print(inv_number)
    item = ItemList.query.filter_by(inv_number=inv_number).first()
    lastIdEvid = Evidenced.query.order_by(Evidenced.id.desc()).first().id 
    evidItem = Evidenced(lastIdEvid+1,inv_id,item.id)
    db.session.add(evidItem)
    db.session.commit()    
    flash(u'Pomyślnie dodano pozycję do spisu!', 'success')
    return redirect(url_for('invent.inv_details',inv_id=inv_id))     

@invent.route('/<int:inv_id>/evidenced/<int:evid_id>/delete', methods=['GET', 'POST'] )
@invent_permissions_required
def inv_evidenced_delete(inv_id, evid_id): 
    evid_item = Evidenced.query.filter_by(id=evid_id, inv_id=inv_id).first()
    db.session.delete(evid_item)
    db.session.commit()
    flash(u'Pomyślnie usunięto pozycję ze spisu!', 'success')
    return redirect(url_for('invent.inv_details',inv_id=inv_id))  

@invent.route('/<int:inv_id>/unknown/add', methods=['GET', 'POST'])
@invent_permissions_required
def inv_unknown_add(inv_id):
    inv_number = request.form.get('inv_number')
    unk_loc = request.form.get('unk_loc')
    unk_desc = request.form.get('unk_desc')
    lastIdUnknown = Unknown.query.order_by(Unknown.id.desc()).first().id 
    db.session.add(Unknown(lastIdUnknown+1,inv_id,inv_number,unk_loc,unk_desc))
    db.session.commit()
    return redirect(url_for('invent.inv_details',inv_id=inv_id)) 

@invent.route('/<int:inv_id>/unknown/<int:unk_id>/delete', methods=['GET', 'POST'] )
@invent_permissions_required
def inv_unknown_delete(inv_id, unk_id): 
    unk_item = Unknown.query.filter_by(id=unk_id, inv_id=inv_id).first()
    db.session.delete(unk_item)
    db.session.commit()
    flash(u'Pomyślnie usunięto pozycję ze spisu!', 'success')
    return redirect(url_for('invent.inv_details',inv_id=inv_id))

@invent.route('/<int:inv_id>/edit', methods=['GET', 'POST'])
@admin_required
def inv_edit(inv_id):
    stocktaking = Stocktaking.query.get_or_404(inv_id)
    
    if request.method == 'POST':
        members = []
        print(request.form.getlist('comMember'))
        for i in range(len(request.form.getlist('comMember'))):
            members.append(request.form.getlist('comMember')[i])
        print(members)
        stocktaking.localization = request.form.get('localization')
        stocktaking.mpk_number = request.form.get('mpkNumber')
        stocktaking.commissioner = request.form.get('commissioner')   
        stocktaking.com_members = members
        db.session.add(stocktaking)
        db.session.commit() 
        flash(u'Pomyślnie edytowano inwentaryzację!','success')
        return redirect(url_for('invent.inv_details',inv_id=stocktaking.id))
    return render_template('inv-edit.html', inv=stocktaking)

@invent.route('/<int:inv_id>/finish', methods=['GET', 'POST'])
@admin_required
def inv_finish(inv_id):
    stocktaking = Stocktaking.query.get_or_404(inv_id)
    stocktaking.finished = True
    stocktaking.date_stop = datetime.datetime.now()
    db.session.add(stocktaking)
    print(stocktaking.finished)
    db.session.commit() 
    flash(u'Zakończono inwentaryzację!','success')
    return redirect(url_for('invent.inv_details',inv_id=stocktaking.id))
       
@invent.route('/<int:inv_id>/document/<doc_type>', methods=['GET', 'POST'] )
@invent_permissions_required
def inv_document(inv_id, doc_type):   
    stocktaking = Stocktaking.query.get_or_404(inv_id)
    if doc_type == 'evidenced':
        items = Evidenced.query.filter_by(inv_id=inv_id)
    elif doc_type == 'unknown':    
        items = Unknown.query.filter_by(inv_id=inv_id)
    elif doc_type == 'nonevidenced':
        evidenced = Evidenced.query.filter_by(inv_id=inv_id)
        items_list = ItemList.query
        items_evidenced = []
        item_ids_evidenced = []
        items = []
        for evid in evidenced:
            occur = ItemList.query.get_or_404(evid.item_id)
            items_evidenced.append(EvidencedItemView(evid.id,evid.item_id,occur.inv_number,occur.localization,evid.add_date))
        try:
            for item in items_evidenced:
                item_ids_evidenced.append(item.id)
            for item in items_list:
                if item.id in item_ids_evidenced:
                    pass
                else:
                    items.append(item)
        except:
            pass 
        print(items) 
    else:
        pass        
    return render_template('pdf-template.html', stocktaking=stocktaking, items=items, doc_type=doc_type)

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
@invent_permissions_required
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
@invent_permissions_required
def inv_task_finish(inv_id,task_id):
    task = Schedule.query.filter_by(inv_id=inv_id,id=task_id).first()
    task.date_end = datetime.datetime.now()
    task.finished = True
    db.session.commit()
    flash(u'Pomyślnie edytowano zadanie!','success')
    return redirect(url_for('invent.inv_schedule', inv_id=inv_id))

@invent.route('/<int:inv_id>/schedule/retrieve/<int:task_id>/', methods=['GET', 'POST'])
@invent_permissions_required
def inv_task_retrieve(inv_id,task_id):
    task = Schedule.query.filter_by(inv_id=inv_id,id=task_id).first()
    task.finished = False
    db.session.commit()
    flash(u'Pomyślnie edytowano zadanie!','success')
    return redirect(url_for('invent.inv_schedule', inv_id=inv_id))  

@invent.route('/<int:inv_id>/schedule/addtask/', methods=['GET', 'POST'])
@invent_permissions_required
def inv_task_add(inv_id): 
    form = forms.AddTask(request.form)
    lastId = Schedule.query.order_by(Schedule.id.desc()).first().id
    print(lastId)
    if request.method == 'POST':
        if form.onetimer.data == False:
            task = Schedule(lastId+1,inv_id,form.date_start.data, form.date_exp_end.data,form.task.data)
        else:
            task = Schedule(lastId+1,inv_id,form.date_start.data, form.date_start.data,form.task.data)
        db.session.add(task)
        db.session.commit()
        flash(u'Dodano zadanie!', 'success')
        return redirect(url_for('invent.inv_schedule',inv_id=inv_id))
    return render_template('inv-add-task.html', form=form)    

@invent.route('/<int:inv_id>/schedule/edit/<int:task_id>/', methods=['GET', 'POST'])
@invent_permissions_required
def inv_task_edit(inv_id,task_id):      
    task = Schedule.query.filter_by(inv_id=inv_id,id=task_id).first()
    form = forms.AddTask(request.form)
    if request.method == 'POST':
        task.date_start = form.date_start.data
        if form.onetimer.data == False:
            task.date_exp_end = form.date_exp_end.data
        else:
            task.date_exp_end = form.date_start.data    
        task.task = form.task.data
        db.session.add(task)
        db.session.commit()
        flash(u'Pomyślnie edytowano zadanie!','success')
        return redirect(url_for('invent.inv_schedule',inv_id=inv_id))
    form.date_start.data = task.date_start
    form.date_exp_end.data = task.date_exp_end
    form.task.data = task.task
    return render_template("inv-add-task.html", form=form, task=task, title=u"Edytuj zadanie") 

@invent.route('/<int:inv_id>/schedule/delete/<int:task_id>/')
@invent_permissions_required
def inv_task_delete(inv_id,task_id):
    task = Schedule.query.filter_by(inv_id=inv_id,id=task_id).first()
    db.session.delete(task)
    db.session.commit()
    flash(u'Pomyślnie usunięto zadanie!', 'danger')
    return redirect(url_for('invent.inv_schedule', inv_id=inv_id))      
