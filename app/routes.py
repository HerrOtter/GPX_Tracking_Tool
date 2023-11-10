from flask import render_template, request
from app import app, db
from app.models import Person, Vehicle, Track, Trackpoint, Protocol
import os
import gpxpy

@app.route('/')
def home():
    function.create_tables()
    tables_are_valid = function.test_created_tables()

    if not tables_are_valid:
        print("The tables were not created successfully. Please check the database and try again.")
        exit()
    else:
        function.import_gpx_files()
    
    return render_template('index.html')

def tracking():
    if request.method == 'POST':
        # Get form data from request
        initials = request.form['nick']
        license_plate = request.form['kfz']

        # Execute query using SQLAlchemy
        trackpoints = (
            db.session.query(Trackpoint.latitude, Trackpoint.longitude, Trackpoint.elevation)
            .join(Track, Track.id == Trackpoint.track_id)
            .join(Person, Person.id == Track.person_id)
            .join(Vehicle, Vehicle.id == Track.vehicle_id)
            .filter(Person.initials == initials, Vehicle.license_plate == license_plate)
            .filter(Protocol.is_valid == '1')
            .all()
        )

        for trackpoint in trackpoints:
            print(trackpoint)

        # Convert trackpoints to coordinates list and render template
        coordinates = [(track[0], track[1]) for track in trackpoints]
        return render_template('index.html', coordinates=coordinates)