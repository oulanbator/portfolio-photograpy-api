# Utilities
import time, json, secrets, os
from PIL import Image as PilImage
import cv2
# Flask imports
from flask import request, url_for
from flask_cors import cross_origin
from flask_login import login_user, current_user, logout_user, login_required
# API package imports
from api import app, db, bcrypt
from api.models import Image, Gallery, User

# Main route (API index)
@app.route('/')
def index():
    return "API INDEX"

# def get_gallery_sources(galleryName):
#     dbGallery = Gallery.query.filter_by(title=galleryName).first()
#     dbSources = []
#     for img in dbGallery.images:
#         title = img.title
#         src = img.source
#         imgDict = {"title": title, "src": src}
#         dbSources.append(imgDict)
#     return dbSources

# ROUTES
@app.route('/api/createGallery')
@cross_origin()
@login_required
def create_gallery():
    # Get title back from args
    title = request.args.get('title')
    # Look for an existing gallery with the same name
    gallery_exists = Gallery.query.filter_by(title=title).first()
    # If gallery name already taken, send back abort status
    if gallery_exists:
        return json.dumps({"status": "aborted"})
    else:
        # Else, create new gallery, add to db, commit and returns success
        newGallery = Gallery(title=title)
        db.session.add(newGallery)
        db.session.commit()
        return json.dumps({"status": "success"})

@app.route('/api/deleteGallery/<name>')
@cross_origin()
@login_required
def delete_gallery(name):
    # Look for gallery in database
    targetGallery = Gallery.query.filter_by(title=name).first()
    # If gallery found, delete from database
    if targetGallery:
        db.session.delete(targetGallery)
        # Commit and returns success
        db.session.commit()
        return json.dumps({"status": "success"})
    # Else, returns failed status
    else:
        return json.dumps({"status": "failed"})

@app.route('/api/saveGallery', methods=['GET', 'POST'])
@cross_origin()
@login_required
def save_gallery():
    if request.method == "POST":
        # Get form informations back from the posted form
        originalTitle = request.form.get('originalTitle')
        title = request.form.get('title')
        firstImage = request.form.get('cover')
        description = request.form.get('description')
        rawImages = request.form.get('images')
        # debug : if rawImage list from form > 2 (2 => unparsed two quotes ['']), then there are images inside
        if len(rawImages) > 2:
            images = rawImages.split(",")
        else:
            images = []
        # If title changed
        if title != originalTitle:
            # look for gallery with the new title
            exists = Gallery.query.filter_by(title=title).first()
            # if a gallery found, the title is already taken => abort
            if exists:
                return json.dumps({"status": "aborted"})
            else:
                # Get the gallery back (thus, with original title)
                gallery = Gallery.query.filter_by(title=originalTitle).first()
        else:
            # If title unchanged, get the gallery back with title
            gallery = Gallery.query.filter_by(title=title).first()
        # Update gallery info
        gallery.title = title
        gallery.firstImage = firstImage
        gallery.description = description
        # remove old images
        # Loop on gallery image
        for img in gallery.images:
            # if image in gallery is also in the new set of images, remove from the list to process
            if img.source in images:
                images.remove(img.source)
            # if image in gallery is not in the new set, delete from the gallery
            else:
                gallery.del_image(img)
        # Add new images
        # Loop on images to process
        for img in images:
            # find the image in database...
            db_image = Image.query.filter_by(source=img).first()
            # And add it to the gallery
            gallery.add_image(db_image)
        # Commit and returns status
        db.session.commit()
    return json.dumps({"status": "success"})

@app.route('/api/galleries')
@cross_origin()
def get_galleries():
    # Get all galleries back
    db_galleries = Gallery.query.all()
    dbSources = []
    # For each...
    for gallery in db_galleries:
        # Get gallery informations
        title = gallery.title
        firstImage = gallery.firstImage
        description = gallery.description
        # Build dict and append to sources list
        imgDict = {"title": title, "firstImage": firstImage, "description": description}
        dbSources.append(imgDict)
    # Transform into json object, and returns it
    sources_js = json.dumps(dbSources)
    return sources_js

@app.route('/api/galleryInfo/<name>')
@cross_origin()
def get_gallery_info(name):
    # Look for gallery in database
    dbGallery = Gallery.query.filter_by(title=name).first()
    # If gallery exists, returns dict with gallery info
    if dbGallery:
        responseDict = {
            "status": "success",
            "title": dbGallery.title,
            "firstImage": dbGallery.firstImage,
            "description": dbGallery.description
        }
        return responseDict
    # Else, returns failed status
    else:
        return json.dumps({"status": "failed"})

@app.route('/api/gallery/<name>')
@cross_origin()
def get_gallery(name):
    # Look for gallery in database
    dbGallery = Gallery.query.filter_by(title=name).first()
    # Build list for image sources
    dbSources = []
    # For each image in gallery
    for img in dbGallery.images:
        # Get image informations back
        title = img.title
        src = img.source
        # Build image dict and append to list 
        imgDict = {"title": title, "src": src}
        dbSources.append(imgDict)
    # Returns JSON object of the list
    return json.dumps(dbSources)

# LOGIN REQUIRED ?? Check in React App
@app.route('/api/medias')
@cross_origin()
def get_medias():
    # Get all images back from database
    db_medias = Image.query.all()
    dbSources = []
    # For each image...
    for img in db_medias:
        # Get informations back
        title = img.title
        src = img.source
        # Build image dict and append to sources list
        imgDict = {"title": title, "src": src}
        dbSources.append(imgDict)
    # Returns JSON object of the list
    return json.dumps(dbSources)

@app.route('/api/medias/delete/<filename>')
@cross_origin()
@login_required
def delete_media(filename):
    # Look for image in database
    media = Image.query.filter_by(source=filename).first()
    # If media is used in one or more galleries
    if media.is_used():
        # Build "abort" response dict with the list of galleries where the image is used
        responseDict = {
            "status": "aborted",
            "galleries": media.is_used()
        }
        # return json object of the dict
        return json.dumps(responseDict)
    # Else, proceed, delete media from database and commit
    else:
        db.session.delete(media)
        db.session.commit()
        # Build image path and delete image from filesystem
        os_path = os.path.join("images/", filename)
        os.remove(os_path)
        return json.dumps({"status": "success"})

@app.route('/api/medias/rotate/<filename>')
@cross_origin()
@login_required
def rotate_media(filename):
    # Look for image in database
    db_image = Image.query.filter_by(source=filename).first()
    if db_image:
        # Build image path
        os_path = os.path.join("images/", filename)
        src = cv2.imread(os_path)
        # Rotation and save on same path
        image = cv2.rotate(src, cv2.cv2.ROTATE_90_CLOCKWISE)
        cv2.imwrite(os_path, image)
    return json.dumps({"status": "success", "source": filename})

@app.route('/api/uploadFile', methods=['GET', 'POST'])
@cross_origin()
@login_required
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
            picture_path = os.path.join("images/", picture_filename)
            # Resize image
            output_size = (600, 600)
            img = PilImage.open(form_picture)
            img.thumbnail(output_size)
            # Save image in filesystem
            img.save(picture_path)
            # add to database
            db_image = Image(source=picture_filename)
            db.session.add(db_image)
        # COMMIT OUTSIDE OF THE LOOP ?
        db.session.commit()
        return json.dumps({"status": "success"})
    
@app.route('/api/login', methods=['GET', 'POST'])
@cross_origin()
def login():
    # If there is a current_user authenticated, returns "already-login" status
    if current_user.is_authenticated:
        return json.dumps({"status": "already-login"})
    if request.method == 'POST':
        # Get data back from posted form
        form_email = request.form.get('email')
        form_password = request.form.get('password')
        form_remember = request.form.get('remember')
        # Look for user in database
        user = User.query.filter_by(email=form_email.lower()).first()
        # if user exists, and password match with encrypted password in database
        if user and bcrypt.check_password_hash(user.password, form_password):
            # Log user and remember user (or not) 
            login_user(user, remember=form_remember)
            # returns success status
            return json.dumps({"status": "login-success"})
        # if user does not exist or password mismatch, returns failed status 
        else:
            return json.dumps({"status": "login-failed"})
    # if endpoint requested through get method, returns error
    return json.dumps({"status": "error-get-request"})

@app.route('/api/logout')
@cross_origin()
@login_required
def logout():
    # if endpoint fetched, logout current user and returns logout status
    logout_user()
    return json.dumps({"status": "logout-success"})
