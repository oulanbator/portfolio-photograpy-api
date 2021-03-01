from api import db, login_manager
from flask_login import UserMixin

# MODELS

galleryImages = db.Table('galleryImages',
    db.Column('galleryId', db.Integer, db.ForeignKey('gallery.id'), primary_key=True),
    db.Column('imageId', db.Integer, db.ForeignKey('image.id'), primary_key=True)
)

class Image(db.Model):
    __tablename__ = 'image'
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String, unique=True, nullable=False)
    title = db.Column(db.String)

    def is_used(self):
        i = 0
        galleries = []
        for gallery in self.galleries:
            galleries.append(gallery.title)
            i += 1
        dbGalleries = Gallery.query.all()
        for gallery in dbGalleries:
            if self.source == gallery.firstImage:
                galleryName = gallery.title
                if galleryName not in galleries:
                    galleries.append(galleryName)
                    i += 1
        if i > 0:
            return galleries
        else:
            return False

class Gallery(db.Model):
    __tablename__ = 'gallery'
    id = db.Column(db.Integer, primary_key=True)
    firstImage = db.Column(db.String, nullable=False, default="default.png")
    title = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String, default="")
    images = db.relationship('Image', secondary=galleryImages, lazy='dynamic',
        backref=db.backref('galleries', lazy='dynamic'))
    
    def add_image(self, image):
        if not self.is_used(image):
            self.images.append(image)

    def del_image(self, image):
        if self.is_used(image):
            self.images.remove(image)

    def is_used(self, image):
        return self.images.filter(
            galleryImages.c.imageId == image.id).count() > 0


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)