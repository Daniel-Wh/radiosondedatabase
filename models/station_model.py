from db import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


class StationModel(db.Model):

    __tablename__ = 'stations'
    id = db.Column(db.INTEGER, primary_key=True)
    name = db.Column(db.String(15))
    lat = db.Column(db.REAL)
    lon = db.Column(db.REAL)
    children = db.relationship("StationData")

    def __init__(self, name, lat, lon):
        self.name = name
        self.lat = lat
        self.lon = lon

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


class StationData(db.Model):

    __tablename__ = 'station_data'

    id = db.Column(db.INTEGER, primary_key=True)
    date = db.Column(db.INTEGER)
    oni = db.Column(db.INTEGER)
    height = db.Column(db.INTEGER)
    temp = db.Column(db.REAL)
    station_id = db.Column(db.INTEGER, ForeignKey('stations.id'))
    station = db.relationship('StationModel')

    def __init__(self, date, oni, height, temp, station_id):
        self.date = date
        self.oni = oni
        self.height = height
        self.temp = temp
        self.station_id = station_id

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


if __name__ == '__main__':
    from app import app
    db.init_app(app)
    db.create_all()
