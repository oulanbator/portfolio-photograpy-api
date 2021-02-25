import time
from flask import request, url_for
from flask_cors import cross_origin
import json
from PIL import Image as PilImage
import secrets, os
# API imports
from api import app, db
from api.models import Image, Gallery

# Main route (React index)
@app.route('/')
def index():
    return app.send_static_file('index.html')

def get_gallery_sources(galleryName):
    dbGallery = Gallery.query.filter_by(title=galleryName).first()
    dbSources = []
    for img in dbGallery.images:
        title = img.title
        src = img.source
        imgDict = {"title": title, "src": src}
        dbSources.append(imgDict)
    return dbSources

# ROUTES 

@app.route('/api/createGallery')
@cross_origin()
def create_gallery():
    title = request.args.get('title')
    firstImage = request.args.get('firstImage')
    gallery_exists = Gallery.query.filter_by(title=title).first()
    if gallery_exists:
        return json.dumps({"status": "aborted"})
    else:
        newGallery = Gallery(title=title, firstImage=firstImage)
        db.session.add(newGallery)
        db.session.commit()
        galleries = get_galleries()
        responseDict = {
            "status": "success",
            "galleries": galleries
        }
        return json.dumps(responseDict)

@app.route('/api/deleteGallery/<name>')
@cross_origin()
def delete_gallery(name):
    targetGallery = Gallery.query.filter_by(title=name).first()
    db.session.delete(targetGallery)
    db.session.commit()
    galleries = get_galleries()
    responseDict = {
        "status": "success",
        "galleries": galleries
    }
    return json.dumps(responseDict)

@app.route('/api/saveGallery', methods=['GET', 'POST'])
@cross_origin()
def save_gallery():
    if request.method == "POST":
        print(request.form)
        # Get form informations back
        originalTitle = request.form.get('originalTitle')
        title = request.form.get('title')
        firstImage = request.form.get('cover')
        description = request.form.get('description')
        rawImages = request.form.get('images')
        print("raw : ", rawImages)
        if len(rawImages) > 2:
            images = rawImages.split(",")
        else:
            images = []
        print(images)
        # Find gallery in Database
        if title != originalTitle:
            # look for gallery with the same title
            exists = Gallery.query.filter_by(title=title).first()
            if exists:
                return json.dumps({"status": "aborted"})
            else:
                # Get the gallery back with original title
                gallery = Gallery.query.filter_by(title=originalTitle).first()
        else:
            # Get the gallery back with title
            gallery = Gallery.query.filter_by(title=title).first()
        # Update gallery
        gallery.title = title
        gallery.firstImage = firstImage
        gallery.description = description
        print("images before removing : ", images)
        # remove old images
        for img in gallery.images:
            if img.source in images:
                images.remove(img.source)
            else:
                gallery.del_image(img)
        # Add new images
        print("images after removing : ", images)
        for img in images:
            # find the image in database, and add it
            db_image = Image.query.filter_by(source=img).first()
            gallery.add_image(db_image)
        db.session.commit()
    return json.dumps({"status": "success"})

@app.route('/api/galleries')
@cross_origin()
def get_galleries():
    db_galleries = Gallery.query.all()
    dbSources = []
    for gallery in db_galleries:
        title = gallery.title
        firstImage = gallery.firstImage
        imgDict = {"title": title, "firstImage": firstImage}
        dbSources.append(imgDict)
    sources_js = json.dumps(dbSources)
    return sources_js

@app.route('/api/galleryInfo/<name>')
@cross_origin()
def get_gallery_info(name):
    # Get Gallery object
    dbGallery = Gallery.query.filter_by(title=name).first()
    responseDict = {
        "status": "success",
        "title": dbGallery.title,
        "firstImage": dbGallery.firstImage,
        "description": dbGallery.description
    }
    return responseDict

@app.route('/api/gallery/<name>')
@cross_origin()
def get_gallery(name):
    print("GALLERY NAME : " + name)
    # Get Gallery object
    dbGallery = Gallery.query.filter_by(title=name).first()
    # Get and build image sources
    dbSources = []
    for img in dbGallery.images:
        title = img.title
        src = img.source
        imgDict = {"title": title, "src": src}
        dbSources.append(imgDict)
    sources_js = json.dumps(dbSources)
    return sources_js

@app.route('/api/medias')
@cross_origin()
def get_medias():
    db_medias = Image.query.all()
    dbSources = []
    for img in db_medias:
        title = img.title
        src = img.source
        imgDict = {"title": title, "src": src}
        dbSources.append(imgDict)
    sources_js = json.dumps(dbSources)
    return sources_js

@app.route('/api/medias/delete/<filename>')
@cross_origin()
def delete_media(filename):
    # Delete image from database
    media = Image.query.filter_by(source=filename).first()
    # If media is used in one or more galleries, return json with status and the list 
    if media.is_used():
        responseDict = {
            "status": "aborted",
            "galleries": media.is_used()
        }
        return json.dumps(responseDict)
    # Else, proceed
    else:
        db.session.delete(media)
        db.session.commit()
        # Delete image from filesystem
        os_path = os.path.join("images/", filename)
        # os_path = "../public/images/" + filename
        os.remove(os_path)
        return json.dumps({"status": "success"})

@app.route('/api/uploadFile', methods=['GET', 'POST'])
@cross_origin()
def uploadFile():
    if request.method == "POST":
        for i in request.files:
            form_picture = request.files[str(i)]
            # Create hexa filename
            random_hex = secrets.token_hex(8)
            # Get extension of the file
            _, f_ext = os.path.splitext(form_picture.filename)
            # build new filename
            picture_filename = random_hex + f_ext
            # Build path
            # picture_path = os.path.join(current_app.root_path, "static/profile_pics", picture_fn)
            picture_path = os.path.join("images/", picture_filename)
            # Resize image
            output_size = (600, 600)
            img = PilImage.open(form_picture)
            img.thumbnail(output_size)
            # Save image in filesystem
            img.save(picture_path)
            print("file saved !")
            # add to database
            db_image = Image(source=picture_filename)
            db.session.add(db_image)
            # COMMIT OUTSIDE OF THE LOOP ?
            db.session.commit()
        return json.dumps({"status": "success"})
    
