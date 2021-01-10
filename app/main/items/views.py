import os, glob, re, shutil
from pathlib import Path
from flask import render_template, request, redirect, url_for, flash, send_from_directory, abort, send_file
from werkzeug.utils import secure_filename
from . import items, forms
from app import app, db
from app.models import Item, ItemList, Comment, Generator, Evidenced
from ..comments.forms import CommentForm
from ..decorators import permissions_required, admin_required
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

def generator(index_nbr):
    if index_nbr == 'item':
        initial_value = '1000010000000'
        try:
            last_value = Generator.query.order_by(Generator.generated_value.desc()).first().generated_value
            if last_value >= '9999990000000':
                return 0
            else:   
                new_value = str(int(last_value[:6]) + 1) + '0000000'
                while True:
                    if ItemList.query.filter(ItemList.inv_number.like(new_value[:6]+'%')).first() == None:
                        break  
                    else:
                        new_value = str(int(nev_value[:6]) + 1) + '0000000'

                generate = Generator(new_value)
                return generate
        except:
            generate = Generator(initial_value)
            return generate
    else:
        last_value = Generator.query.filter(Generator.generated_value.like(index_nbr[:6]+'%')).order_by(Generator.generated_value.desc()).first().generated_value
        print(last_value)
        if last_value[6:] == '9999999':
            return 0
        else:   
            new_value = str(int(last_value)+1)
            print(new_value)
            while True:
                if ItemList.query.filter_by(inv_number=str(new_value)).first() == None:
                    break  
                else:
                    new_value = str(int(new_value)+1)  

            generate = Generator(new_value)
            return generate          

@items.route('/add', methods=['GET', 'POST'] )
def add():
    form = forms.AddItemForm(request.form)
    generated_value = generator('item')
    if form.validate_on_submit():
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
    return render_template('add-item.html', form=form, generated_value=generated_value.generated_value, edit=0)

@items.route('/<int:item_id>/edit/', methods=['GET', 'POST'])    
@admin_required
def edit(item_id):
    item = Item.query.get_or_404(item_id)
    form = forms.AddItemForm(request.form)
    if form.validate_on_submit():
        item.name = form.name.data
        item.index_nbr = form.index_nbr.data
        item.description = form.description.data
        db.session.add(item)
        db.session.commit()
        flash(u'Pomyślnie edytowano pozycję!','warning')
        return redirect(url_for('items.index'))
    form.name.data = item.name
    form.index_nbr.data = item.index_nbr
    form.description.data = item.description  
    return render_template("add-item.html", form=form, item=item, edit=1)  

@items.route('/<int:item_id>/delete/')
@admin_required
def delete(item_id):
    item = Item.query.get_or_404(item_id)
    occurrences = ItemList.query.filter_by(item_id=item.id)
    for occur in occurrences:
        occurrence_remover_func(occur.id)
    db.session.delete(item)
    db.session.commit()
    flash(u'Pomyślnie usunięto pozycję!', 'danger')
    return redirect(url_for('items.index'))    

@items.route('<int:item_id>/occurrence/add', methods=['GET', 'POST'])
def add_occurrence(item_id):
    form = forms.AddOccurrenceForm()
    item = Item.query.get_or_404(item_id)
    if len(item.index_nbr) == 13 and item.index_nbr.isdigit():
        generated_inv_number = generator(item.index_nbr)
        print(generated_inv_number)
    else:
        generated_inv_number = 0    
    if request.method == 'POST' and form.validate_on_submit():
        filename_img = re.sub('[^a-zA-Z0-9.]','-',secure_filename(form.img.data.filename))
        filename_doc = re.sub('[^a-zA-Z0-9.]','-',secure_filename(form.documents.data.filename))
        dir_name = re.sub('[^a-zA-Z0-9.]','-',form.inv_number.data)
        if filename_img != "":
            file_ext = os.path.splitext(filename_img)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS_PHOTOS']:
                abort(400)
            Path(app.config['UPLOADED_PHOTOS_DEST']+dir_name).mkdir()
            form.img.data.save(app.config['UPLOADED_PHOTOS_DEST']+dir_name+'/'+filename_img)
        if filename_doc != "":
            file_ext = os.path.splitext(filename_doc)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS_DOCS']:
                abort(400)
            Path(app.config['UPLOADED_DOCS_DEST']+dir_name).mkdir()
            form.documents.data.save(app.config['UPLOADED_DOCS_DEST']+dir_name+'/'+filename_doc)
        occurrence = ItemList(item_id, form.inv_number.data, form.localization.data,
                    form.img.data.filename, form.documents.data.filename)
        if form.inv_number.data == generated_inv_number.generated_value:
            db.session.add(occurrence) 
            db.session.add(generated_inv_number)
        else:
            db.session.add(occurrence)    
        db.session.commit()
        flash(u'Dodano wystąpienie przedmiotu!', 'success')
        return redirect(url_for('items.details',item_id=item_id))
    return render_template('add-occurrence.html', form=form, generated_value=generated_inv_number.generated_value, edit=0)   

@items.route('/occurrence/<int:occur_id>/details')
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

    #tworzenie kodu kreskowego code128
    barCode = ''
    barCodeFileName = re.sub(re.compile('\W'),"-","temp_ean" + occurrence.inv_number)
    code128 = Code128(occurrence.inv_number, writer=ImageWriter())
    code128.save(app.config['TEMP_CODES_DEST'] + barCodeFileName)
    barCode = '/static/temp/' + barCodeFileName + ".png"
    """
        with open(barCode, 'wb') as f:
            ean = EAN13(occurrence.inv_number, writer=ImageWriter()).write(f)
            fullname = ean.save(barCode)
        """
    """
    tempFileObj = NamedTemporaryFile(mode='w+b',suffix='jpg')
    pilImage = open('/tmp/myfile.jpg','rb')
    copyfileobj(pilImage,tempFileObj)
    pilImage.close()
    remove('/tmp/myfile.jpg')
    tempFileObj.seek(0,0)
    """
    attachment = occurrence.documents
    dir_name = re.sub('[^a-zA-Z0-9.]','-',occurrence.inv_number)
    if os.path.exists(app.config['UPLOADED_PHOTOS_DEST']+dir_name) == True:
        img = '/static/photos/'+dir_name+'/'+occurrence.img
    else:
        img = '/static/img/no-photo.PNG'     # obrazek domyślny w przypadku braku zdjęcia
    comments = occurrence.comments \
            .order_by(Comment.edit_timestamp.desc())    
    return render_template('occurrence-details.html', form=form, occurrence=occurrence, comments=comments, qrCode=qrCode, barCode=barCode, dirname=dir_name, img=img)      

@items.route('/occurrence/<int:occur_id>/edit/', methods=['GET', 'POST'])    
@admin_required
def edit_occurrence(occur_id):
    occurrence = ItemList.query.get_or_404(occur_id)
    form = forms.AddOccurrenceForm()
    if request.method == 'POST' and form.validate_on_submit():
        occurrence.inv_number = form.inv_number.data
        occurrence.localization = form.localization.data
        # pliki
        filename_img = re.sub('[^a-zA-Z0-9.]','-',secure_filename(form.img.data.filename))
        filename_doc = re.sub('[^a-zA-Z0-9.]','-',secure_filename(form.documents.data.filename))
        dir_name = re.sub('[^a-zA-Z0-9.]','-',form.inv_number.data)
        if filename_img != "":
            file_ext = os.path.splitext(filename_img)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS_PHOTOS']:
                abort(400)
            if os.path.exists(app.config['UPLOADED_PHOTOS_DEST']+dir_name): # jesli jest zdjecie to zamieniamy 
                files = glob.glob(app.config['UPLOADED_PHOTOS_DEST']+dir_name+'/*')
                for f in files: 
                    os.remove(f)
                form.img.data.save(app.config['UPLOADED_PHOTOS_DEST']+dir_name+'/'+filename_img)
            else: # jesli nie to tworzymy folder i wrzucamy
                Path(app.config['UPLOADED_PHOTOS_DEST']+dir_name).mkdir()
                form.img.data.save(app.config['UPLOADED_PHOTOS_DEST']+dir_name+'/'+filename_img)
            occurrence.img = filename_img
        if filename_doc != "":
            file_ext = os.path.splitext(filename_doc)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS_DOCS']:
                abort(400)
            if os.path.exists(app.config['UPLOADED_DOCS_DEST']+dir_name): # jesli jest zalacznik to zamieniamy 
                files = glob.glob(app.config['UPLOADED_DOCS_DEST']+dir_name+'/*')
                for f in files:
                    os.remove(f)
                form.documents.data.save(app.config['UPLOADED_DOCS_DEST']+dir_name+'/'+filename_doc)
            else: # jesli nie to tworzymy folder i wrzucamy    
                Path(app.config['UPLOADED_DOCS_DEST']+dir_name).mkdir()
                form.documents.data.save(app.config['UPLOADED_DOCS_DEST']+dir_name+'/'+filename_doc)
            occurrence.documents = filename_doc

        db.session.add(occurrence)
        db.session.commit()
        flash(u'Pomyślnie edytowano wystąpienie!','warning')
        return redirect(url_for('items.occurrence_details',occur_id=occur_id))
    form.inv_number.data = occurrence.inv_number
    form.localization.data = occurrence.localization 
    return render_template("add-occurrence.html", form=form, occurrence=occurrence, title=u"Edytuj pozycję", edit=1)     

def occurrence_remover_func(occur_id):
    occurrence = ItemList.query.get_or_404(occur_id)
    # dodanie wystapienia do usunietych
    deleted_occurrence = ItemList(1,occurrence.inv_number,occurrence.localization,'','')
    db.session.add(deleted_occurrence)
    db.session.flush()
    db.session.refresh(deleted_occurrence)
    # dodanie komentarza o usunietym przedmiocie
    item = Item.query.get_or_404(occurrence.item_id)
    lastId_Comment = Comment.query.order_by(Comment.id.desc()).first().id
    db.session.add(Comment(lastId_Comment+1,deleted_occurrence.id,'Nazwa: '+item.name+' Opis: '+item.description))
    # edycja informacji o wystapieniu przedmiotu w spisach
    evidenced = Evidenced.query.filter_by(item_id=occurrence.id)
    for evid in evidenced:
        evid.item_id = deleted_occurrence.id
        db.session.add(evid)
    # usuniecie komentarzy
    comments_remover_func(occur_id)
    # usuniecie wystapienia przedmiotu
    db.session.delete(occurrence)  
    db.session.commit()   
    # usuniecie zalacznikow 
    try:
        shutil.rmtree(app.config['UPLOADED_DOCS_DEST']+re.sub('[^a-zA-Z0-9.]','-',occurrence.inv_number))
    except:
        pass
    return item.id

def comments_remover_func(occur_id):
    comments = Comment.query.filter_by(item_id=occur_id)
    for comment in comments:
        db.session.delete(comment)       
    return 0  

@items.route('occurrence/<int:occur_id>/delete/')
@admin_required
def delete_occurrence(occur_id):
    item_id = occurrence_remover_func(occur_id)
    db.session.commit()
    flash(u'Pomyślnie usunięto pozycję!', 'danger')
    return redirect(url_for('items.details', item_id=item_id), code=307)        

@items.route('occurrence/download/<inv_number>/<filename>/', methods=['GET', 'POST'])
def download_occurrence_attachment(inv_number,filename):
    docs = os.path.join(app.root_path, app.config['UPLOADED_DOCS_DEST']+re.sub('[^a-zA-Z0-9.]','-',inv_number))
    print(app.config['UPLOADED_DOCS_DEST']+re.sub('[^a-zA-Z0-9.]','-',inv_number)+'/'+filename)
    return send_from_directory(directory=docs, filename=re.sub('[^a-zA-Z0-9.]','-',filename))
