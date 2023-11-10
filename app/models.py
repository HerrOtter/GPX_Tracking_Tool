from app import db

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    initials = db.Column(db.String(2))

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    license_plate = db.Column(db.String(8))

class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'))
    date = db.Column(db.String(10))
    person = db.relationship('Person', backref='tracks')
    vehicle = db.relationship('Vehicle', backref='tracks')

class Trackpoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    track_id = db.Column(db.Integer, db.ForeignKey('track.id'))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    elevation = db.Column(db.Float)
    date = db.Column(db.String(10))
    time = db.Column(db.String(8))
    temperature = db.Column(db.Float)
    hr = db.Column(db.Integer)
    track = db.relationship('Track', backref='trackpoints')

class Protocol(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255))
    track_id = db.Column(db.Integer, db.ForeignKey('track.id'))
    is_valid = db.Column(db.String(1))
    track = db.relationship('Track', backref='protocol')