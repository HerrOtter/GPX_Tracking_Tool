from app import db
from app.models import Person, Vehicle, Track, Trackpoint, Protocol
import os
import gpxpy

def create_tables():
    db.create_all()

def test_created_tables():
    tables = db.engine.table_names()
    
    assert 'person' in tables
    assert 'vehicle' in tables
    assert 'track' in tables
    assert 'trackpoint' in tables
    assert 'protocol' in tables
    
    print("All tables were created successfully.")
    return True

def parse_gpx_file(filename):
    with open(filename, 'r') as gpx_file:
        return gpxpy.parse(gpx_file)

def extract_person_data(filename):
    filename_parts = filename.split("_")
    if len(filename_parts) >= 3:
        initials = filename_parts[0]
        return initials
    else:
        return None

def extract_track_data(filename):
    return filename[:-4]

def extract_vehicle_data(filename):
    filename_parts = filename.split("_")
    if len(filename_parts) >= 3:
        vehicle_license_plate = filename_parts[1]
        vehicle_license_plate = vehicle_license_plate.replace("-", "")
        return vehicle_license_plate
    else:
        return None
    
def import_gpx_files():
    imported_files = set()

    existing_files = Protocol.query.with_entities(Protocol.filename).all()
    for existing_file in existing_files:
        imported_files.add(existing_file[0])

    for filename in os.listdir('./data/gpx'):
        if filename.endswith('.gpx') and filename not in imported_files:
            gpx = parse_gpx_file('./data/gpx/' + filename)

            person_initials = extract_person_data(filename)
            person_id = insert_person_data(person_initials)

            vehicle_license_plate = extract_vehicle_data(filename)
            vehicle_id = insert_vehicle_data(vehicle_license_plate)

            track_filename = extract_track_data(filename)
            track_id = insert_track_data(track_filename, person_id, vehicle_id)

            extract_trackpoint_data(track_id, gpx, filename)

            db.session.commit()

            imported_files.add(filename)

def insert_person_data(initials):
    person_entry = Person(initials=initials)
    db.session.add(person_entry)
    db.session.commit()
    return person_entry.id

def insert_vehicle_data(vehicle_license_plate):
    vehicle_entry = Vehicle(license_plate=vehicle_license_plate)
    db.session.add(vehicle_entry)
    db.session.commit()
    return vehicle_entry.id

def insert_track_data(filename, person_id, vehicle_id):
    track_entry = Track(filename=filename, person_id=person_id, vehicle_id=vehicle_id)
    db.session.add(track_entry)
    db.session.commit()
    return track_entry.id

def extract_trackpoint_data(track_id, gpx, filename):
    print(filename)
    if gpx.tracks is not None:
        if len(gpx.tracks) > 0:
            for track in gpx.tracks:
                if len(track.segments) > 0:
                    for segment in track.segments:
                        for point in segment.points:
                            lat = point.latitude
                            lon = point.longitude
                            ele = point.elevation
                            tp_time = point.time
                            atemp = None
                            hr = None
                            if point.extensions is not None:
                                for extension in point.extensions:
                                    if extension.tag.endswith("TrackPointExtension"):
                                        for child in extension.iter():
                                            if child.tag.endswith("atemp"):
                                                atemp = child.text
                                            elif child.tag.endswith("hr"):
                                                hr = child.text

                            is_valid = lat is not None or lon is not None or ele is not None

                            if not is_valid:
                                is_valid_value = '0'
                                protocol_entry = Protocol(filename=filename, track_id=track_id, is_valid=is_valid_value)
                                db.session.add(protocol_entry)
                                break
                            else:
                                is_valid_value = '1'
                                if tp_time is not None:
                                    tp_time_date = tp_time.date()
                                    tp_time_time = tp_time.time()
                                else:
                                    tp_time_date = None
                                    tp_time_time = None

                                trackpoint_entry = Trackpoint(track_id=track_id, latitude=lat, longitude=lon,
                                                              elevation=ele, date=str(tp_time_date), time=str(tp_time_time),
                                                              temperature=atemp, hr=hr)
                                db.session.add(trackpoint_entry)

                                track_entry = Track.query.get(track_id)
                                track_entry.date = tp_time_date

            if is_valid_value != '0':
                protocol_entry = Protocol(filename=filename, track_id=track_id, is_valid=is_valid_value)
                db.session.add(protocol_entry)

    db.session.commit()
