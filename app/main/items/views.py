import os, glob, re
from flask import render_template, request, redirect, url_for, flash, send_from_directory, abort, send_file
from werkzeug.utils import secure_filename
from . import items, forms
from app import app, db
from app.models import Item, ItemList, Comment
from ..comments.forms import CommentForm
from tempfile import NamedTemporaryFile
from shutil import copyfileobj
import qrcode
from barcode import EAN13
from barcode.writer import ImageWriter

app.config['UPLOAD_FOLDER'] = 'uploads'
@items.route('/uploads/<filename>')
def uploaded_file(filename):
    img_path = app.config['UPLOAD_FOLDER'] + '/images'
    return send_from_directory(img_path,filename)

@items.route('/')
def index():
    the_items = Item.query
    return render_template('items-list.html', items=the_items)

@items.route('/<int:item_id>/details')
def details(item_id):
    item = Item.query.get_or_404(item_id)
    occurrences = ItemList.query.filter_by(item_id=item_id)
    return render_template('item-details.html', item=item, occurrences=occurrences)   

@items.route('/add', methods=['GET', 'POST'] )
def add():
    form = forms.AddItemForm(request.form)
    if request.method == 'POST' and form.validate():
        item = Item(form.name.data, form.index_nbr.data,
                    form.description.data)
        db.session.add(item)
        db.session.commit()
        flash(u'Dodano pozycję!', 'success')
        return redirect(url_for('items.index'))
    return render_template('add-item.html', form=form)

@items.route('/<int:item_id>/edit/', methods=['GET', 'POST'])    
def edit(item_id):
    item = Item.query.get_or_404(item_id)
    form = forms.AddItemForm()
    if form.validate_on_submit():
        item.name = form.name.data
        item.inv_number = form.inv_number.data
        item.description = form.description.data
        db.session.add(item)
        db.session.commit()
        flash(u'Pomyślnie edytowano pozycję!','warning')
        return redirect(url_for('items.index'))
    form.name.data = item.name
    form.inv_number.data = item.inv_number
    form.description.data = item.description  
    return render_template("add-item.html", form=form, item=item, title=u"Edytuj pozycję")  

@items.route('/<int:item_id>/delete/')
def delete(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash(u'Pomyślnie usunięto pozycję!', 'danger')
    return redirect(url_for('items.index', item_id=item_id))    

@items.route('<int:item_id>/occurrence/add', methods=['GET', 'POST'])
def add_occurrence(item_id):
    form = forms.AddOccurrenceForm()
    if request.method == 'POST' and form.validate():
        print(form.inv_number.data)
        print(form.localization.data)
        print(form.documents.data)
        uploaded_file = form.documents.data
        filename = secure_filename(form.documents.data.filename)
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                abort(400)
            uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        occurrence = ItemList(item_id, form.inv_number.data, form.localization.data,
                    form.img.data.filename, form.documents.data.filename)
        db.session.add(occurrence)
        db.session.commit()
        flash(u'Dodano wystąpienie przedmiotu!', 'success')
        return redirect(url_for('items.details',item_id=item_id))
    return render_template('add-occurrence.html', form=form)   

@items.route('/occurence/<int:occur_id>/details')
def occurrence_details(occur_id):
    form = CommentForm()
    occurrence = ItemList.query.get_or_404(occur_id)

    #usuniecie plikow tymczasowych
    for filename in glob.glob('C:/Python Projects/INVOhelper/app/static/img/temp_qr*.png'):
        os.remove(filename)    

    #tworzenie kodu QR
    qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=5)
    qr.add_data(occurrence.inv_number)
    qr.make(fit=True)
    for filename in glob.glob('C:/Python Projects/INVOhelper/app/static/img/temp_qr*.png'):
        os.remove(filename)
    img = qr.make_image(fill='black', back_color='white')
    pattern = re.compile('\W')
    qrFileName = re.sub(re.compile('\W'),"-","qr_temp_" + occurrence.inv_number) + ".png"
    img.save('C:/Python Projects/INVOhelper/app/static/img/' + qrFileName)
    qrCode = '/static/img/' + qrFileName

    #tworzenie kodu kreskowego EAN13
    barCode = ''
    if re.match(pattern="^\d{13}$", string=occurrence.inv_number): 
        canEAN = 1
        barCode = 'C:/Python Projects/INVOhelper/app/static/img/ean_temp_' + occurrence.inv_number + '.png'
        ean = EAN13(occurrence.inv_number, writer=ImageWriter())
        fullname = ean.save(barCode)
        barCode = '/static/img/ean_temp_' + occurrence.inv_number + '.png'
        """
        with open(barCode, 'wb') as f:
            ean = EAN13(occurrence.inv_number, writer=ImageWriter()).write(f)
            fullname = ean.save(barCode)
        """    
    else:
        canEAN = 0
    """
    tempFileObj = NamedTemporaryFile(mode='w+b',suffix='jpg')
    pilImage = open('/tmp/myfile.jpg','rb')
    copyfileobj(pilImage,tempFileObj)
    pilImage.close()
    remove('/tmp/myfile.jpg')
    tempFileObj.seek(0,0)
    """
    attachment = occurrence.documents
    comments = occurrence.comments.filter_by(deleted=0) \
            .order_by(Comment.edit_timestamp.desc())    
    return render_template('occurrence-details.html', form=form, occurrence=occurrence, comments=comments, qrCode=qrCode, canEAN=canEAN, barCode=barCode)      

@items.route('/occurrence/<int:occur_id>/edit/', methods=['GET', 'POST'])    
def edit_occurrence(occur_id):
    occurrence = ItemList.query.get_or_404(occur_id)
    form = forms.AddOccurrenceForm()
    if form.validate_on_submit():
        occurrence.inv_number = form.inv_number.data
        occurrence.localization = form.localization.data
        db.session.add(occurrence)
        db.session.commit()
        flash(u'Pomyślnie edytowano wystąpienie!','warning')
        return redirect(url_for('items.occurrence_details',occur_id=occur_id))
    form.inv_number.data = occurrence.inv_number
    form.localization.data = occurrence.localization 
    return render_template("add-occurrence.html", form=form, occurrence=occurrence, title=u"Edytuj pozycję")     

@items.route('occurrence/<int:occur_id>/delete/')
def delete_occurrence(occur_id):
    occurrence = ItemList.query.get_or_404(occur_id)
    item_id = occurrence.item_id
    db.session.delete(occurrence)
    db.session.commit()
    occurrences = ItemList.query.filter_by(item_id=item_id)
    flash(u'Pomyślnie usunięto pozycję!', 'danger')
    return redirect(url_for('items.details', item_id=item_id, occurrences=occurrences))        

@items.route('occurrence/download/<filename>/', methods=['GET', 'POST'])
def download_occurrence_attachment(filename):
    uploads = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    return send_from_directory(directory=uploads,
                               filename=filename)

@items.route('calendar/')
def calendar():                               
    return render_template('test.html')