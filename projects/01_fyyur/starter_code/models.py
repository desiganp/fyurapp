#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


#----------------------------------------------------------------------------#
# db instantiation
#----------------------------------------------------------------------------#

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    looking_for_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    artists = db.relationship('Artist', secondary='Show',
      backref=db.backref('venues', lazy=True))

    def __repr__(self):
      return f'<Venue {self.id} {self.description}, name {self.name}>'

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    looking_for_venues = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))

    def __repr__(self):
      return f'<Artist {self.id} {self.description}, name {self.name}>'

class Show(db.Model):
   __tablename__='Show'
   id = db.Column(db.Integer, primary_key=True)
   start_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
   artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
   venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)

   def __repr__(self):
      return f'<Show {self.id} {self.description}>'