from api import db

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
        if i > 0:
            return galleries
        else:
            return False

class Gallery(db.Model):
    __tablename__ = 'gallery'
    id = db.Column(db.Integer, primary_key=True)
    firstImage = db.Column(db.String, unique=True, nullable=False)
    title = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String)
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
