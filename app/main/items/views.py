import os, glob, re
from pathlib import Path
from flask import render_template, request, redirect, url_for, flash, send_from_directory, abort, send_file
from werkzeug.utils import secure_filename
from . import items, forms
from app import app, db
from app.models import Item, ItemList, Comment, Generator
from ..comments.forms import CommentForm
from tempfile import NamedTemporaryFile
from shutil import copyfileobj
import qrcode
from barcode import Code128
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

def genetator():
    initial_value = '1000010000000'
    try:
        last_value = Generator.query.order_by(Generator.id.desc()).first().generated_value
        new_value = str(int(last_value[:6]) + 1) + '0000000'
        generate = Generator(new_value)
        return generate   
    except:
        generate = Generator(initial_value)
        return generate

@items.route('/add', methods=['GET', 'POST'] )
def add():
    form = forms.AddItemForm(request.form)
    generated_value = genetator()
    if request.method == 'POST':
        item = Item(form.name.data, form.index_nbr.data,
                    form.description.data)
        if form.index_nbr.data == generated_value.generated_value:
            db.session.add(generated_value)
            db.session.add(item)
        else:
            db.session.add(item)    
        db.session.commit()
        flash(u'Dodano pozycję!', 'success')
        return redirect(url_for('items.index'))
    return render_template('add-item.html', form=form, generated_value=generated_value.generated_value)

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
    item = Item.query.get_or_404(item_id)
    print(app.config['TEMP_CODES_DEST'])
    if len(item.index_nbr) == 13 and item.index_nbr.isdigit():
        generated_inv_number = int(item.index_nbr)+1
    else:
        generated_inv_number = 0    
    if request.method == 'POST' and form.validate_on_submit():
        filename_img = secure_filename(form.img.data.filename)
        filename_doc = secure_filename(form.documents.data.filename)
        if filename_img != "":
            file_ext = os.path.splitext(filename_img)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS_PHOTOS']:
                abort(400)
            Path(app.config['UPLOADED_PHOTOS_DEST']+form.inv_number.data).mkdir()
            form.img.data.save(app.config['UPLOADED_PHOTOS_DEST']+form.inv_number.data+'/'+filename_img)
        if filename_doc != "":
            file_ext = os.path.splitext(filename_doc)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS_DOCS']:
                abort(400)
            Path(app.config['UPLOADED_DOCS_DEST']+form.inv_number.data).mkdir()
            form.documents.data.save(app.config['UPLOADED_DOCS_DEST']+form.inv_number.data+'/'+filename_doc)
        occurrence = ItemList(item_id, form.inv_number.data, form.localization.data,
                    form.img.data.filename, form.documents.data.filename)
        db.session.add(occurrence)
        db.session.commit()
        flash(u'Dodano wystąpienie przedmiotu!', 'success')
        return redirect(url_for('items.details',item_id=item_id))
    return render_template('add-occurrence.html', form=form, generated_value=generated_inv_number)   

@items.route('/occurence/<int:occur_id>/details')
def occurrence_details(occur_id):
    form = CommentForm()
    occurrence = ItemList.query.get_or_404(occur_id)

    #usuniecie plikow tymczasowych
    for filename in glob.glob(app.config['TEMP_CODES_DEST']+'temp_*.png'):
        os.remove(filename)    

    #tworzenie kodu QR
    qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=5)
    qr.add_data(occurrence.inv_number)
    qr.make(fit=True)
    for filename in glob.glob(app.config['TEMP_CODES_DEST']+'qr_temp*.png'):
        os.remove(filename)
    img = qr.make_image(fill='black', back_color='white')
    pattern = re.compile('\W')
    qrFileName = re.sub(re.compile('\W'),"-","temp_qr" + occurrence.inv_number) + ".png"
    img.save(app.config['TEMP_CODES_DEST'] + qrFileName)
    qrCode = '/static/temp/' + qrFileName

    #tworzenie kodu kreskowego EAN13
    barCode = ''
    if re.match(pattern="^\d{13}$", string=occurrence.inv_number): 
        print(occurrence.inv_number)
        canEAN = 1
        barCodeFileName = re.sub(re.compile('\W'),"-","temp_ean" + occurrence.inv_number)
        ean = Code128(occurrence.inv_number, writer=ImageWriter())
        ean.save(app.config['TEMP_CODES_DEST'] + barCodeFileName)
        barCode = '/static/temp/' + barCodeFileName + ".png"
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

@items.route('occurrence/download/<inv_number>/<filename>/', methods=['GET', 'POST'])
def download_occurrence_attachment(inv_number,filename):
    docs = os.path.join(app.root_path, app.config['UPLOADED_DOCS_DEST']+inv_number)
    return send_from_directory(directory=docs,
                               filename=filename)

@items.route('calendar/')
def calendar():                               
    return render_template('test.html')