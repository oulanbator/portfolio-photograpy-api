import time
from flask import request, url_for
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

@app.route('/api/gallery/<name>')
def get_gallery(name):
    sources = get_gallery_sources(name)
    sources_js = json.dumps(sources)
    return sources_js

@app.route('/api/medias')
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
def delete_media(filename):
    # Delete image from database
    path = "images/" + filename
    media = Image.query.filter_by(source=path).first()
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
        image_file = filename
        os_path = url_for('static', filename="images/" + image_file)
        # os_path = "../public/images/" + filename
        os.remove(os_path)
        return json.dumps({"status": "success"})

@app.route('/api/uploadFile', methods=['GET', 'POST'])
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
            picture_path = os.path.join("../public/images/", picture_filename)
            # Resize image
            output_size = (600, 600)
            img = PilImage.open(form_picture)
            img.thumbnail(output_size)
            # Save image in filesystem
            img.save(picture_path)
            print("file saved !")
            # add to database
            db_picture_path = os.path.join("images/", picture_filename)
            db_image = Image(source=db_picture_path)
            db.session.add(db_image)
            # COMMIT OUTSIDE OF THE LOOP ?
            db.session.commit()
        return "True"
    
