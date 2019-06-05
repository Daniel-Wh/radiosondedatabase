from db import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, scoped_session, sessionmaker

DBSession = scoped_session(sessionmaker())


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
    year = db.Column(db.INTEGER)
    month = db.Column(db.INTEGER)
    day = db.Column(db.INTEGER)
    oni = db.Column(db.INTEGER)
    height = db.Column(db.INTEGER)
    temp = db.Column(db.REAL)
    time = db.Column(db.INTEGER)
    station_id = db.Column(db.INTEGER, ForeignKey('stations.id'))
    station = db.relationship('StationModel')

    def __init__(self, year, month, day, oni, height, temp, time, station_id):
        self.year = year
        self.month = month
        self.day = day
        self.oni = oni
        self.height = height
        self.temp = temp
        self.time = time
        self.station_id = station_id

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


class OniData(db.Model):

    __tablename__ = 'adjusted_oni'

    id = db.Column(db.INTEGER, primary_key=True)
    year = db.Column(db.INTEGER)
    month = db.Column(db.INTEGER)
    oni = db.Column(db.INTEGER)

    def __init__(self, year, month, oni):
        self.year = year
        self.month = month
        self.oni = oni

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_date(cls, year, month):
        row = db.session.query(cls).filter(OniData.year == year).filter(OniData.month == month).first()
        oni = row.oni
        return oni


if __name__ == '__main__':
    from app import app
    db.init_app(app)
    db.create_all()
