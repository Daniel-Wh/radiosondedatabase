from radiosonde.db import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker
from dateutil.relativedelta import *
from datetime import datetime

DBSession = scoped_session(sessionmaker())


class JustReadings(db.Model):
    # create new table for just the readings (elevation at lowest temp) that will be used in visualizations
    __tablename__ = 'just_readings'
    # id will be primary key(unique)
    id = db.Column(db.Integer, primary_key=True)
    # station is stored as string with no more than 11 characters
    station = db.Column(db.String(11))
    # date is stored as DateTime format which is how it comes from siphon
    date = db.Column(db.DateTime)
    # elevation at lowest temperature for this launch
    height = db.Column(db.Integer)
    # Oceanic Nino Index, needed for grouping data
    oni = db.Column(db.Integer)

    def __init__(self, station_name, date, reading, oni):
        self.station = station_name
        self.date = date
        self.height = reading
        self.oni = oni

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_readings_no_oni(cls, station_name, begin_date, end_date):
        readings = []
        while begin_date != end_date:
            row = db.session.query(cls).filter(cls.date == begin_date).filter(cls.station == station_name).first()
            if row is None:
                print('skip')
            else:
                readings.append(row.height)
            begin_date = begin_date + relativedelta(days=1)
        # because relative delta offers an increase in each iteration by day, the method will isolate
        # values by launch hou
        return readings

    @classmethod
    def create_monthly_averages(cls, missing_date, station_name):
        # initialize empty list for readings
        readings = []
        # creates new date starting on the first of the month for the given missing date
        date = datetime(missing_date.year, missing_date.month, 1, missing_date.hour)
        # end date for while loop that is one month and one day to capture the full month of data
        end_date = date + relativedelta(days=+1, months=+1)
        while date != end_date:
            # queries row in database - skips if none, appends height to reading list to find average later
            row = db.session.query(cls).filter(cls.date == date).filter(cls.station == station_name).first()
            if row is None:
                date = date + relativedelta(days=+1)
                print('Skip')
            elif row.height is None:
                date = date + relativedelta(days=+1)
                print('Skip')
            else:
                readings.append(row.height)
                date = date + relativedelta(days=+1)

        year_month = datetime(missing_date.year, missing_date.month, 1, missing_date.hour)
        average = 0
        if len(readings) > 0:
            average = round(sum(readings)/len(readings), 0)
            print('Average for year {}/{} is {}'.format(year_month.year, year_month.day, average))
            for_db = UpdatedMonthly(station_name=station_name, average=average, year_month=year_month,
                                    oni=OniData.find_by_date(missing_date.year, missing_date.month))
            for_db.save_to_db()

        return average

    @classmethod
    def get_readings_by_season(cls):
        # isolate readings for given season
        return -1

    @classmethod
    def get_readings_with_oni(cls, begin_date, end_date, station_name, oni):
        # isolate readings by station and oceanic nino index
        return -1


class UpdatedMonthly(db.Model):
    # creating class/table for monthly averages by station
    __tablename__ = 'UpdatedMonthly'
    id = db.Column(db.Integer, primary_key=True)
    # station name
    station = db.Column(db.String(11))
    # date - will only every b year/month/hour to separate 00/12 hour launches
    date = db.Column(db.DateTime)
    # average for that month at 00/12 hour
    height_average = db.Column(db.Integer)
    # oceanic nino index for that month
    oni = db.Column(db.Integer)

    def __init__(self, station_name, year_month, average, oni):
        self.station = station_name
        self.date = year_month
        self.height_average = average
        self.oni = oni

    @classmethod
    def get_monthly_average_no_oni(cls, station_name, date):
        for_query_date = datetime(date.year, date.month, 1, date.hour)
        row = db.session.query(cls).filter(cls.station == station_name).filter(cls.date == for_query_date).first()
        if row is None:
            return -1

        return row.height_average

    @classmethod
    def get_monthly_average_w_oni(cls, station_name, date, oni):
        # created method for future construction
        return -1

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


class StationModel(db.Model):

    __tablename__ = 'stations'
    id = db.Column(db.INTEGER, primary_key=True)
    name = db.Column(db.String(15))
    lat = db.Column(db.REAL)
    lon = db.Column(db.REAL)
    children = db.relationship("Launch")

    def __init__(self, name, lat, lon):
        self.name = name
        self.lat = lat
        self.lon = lon

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()


class Launch(db.Model):

    __tablename__ = 'launch'

    id = db.Column(db.INTEGER, primary_key=True)
    date = db.Column(db.DateTime)
    oni = db.Column(db.INTEGER)
    station_id = db.Column(db.INTEGER, ForeignKey('stations.id'))
    station = db.relationship('StationModel')
    children = db.relationship('Reading')

    def __init__(self, date, oni, station_id):
        self.date = date
        self.oni = oni
        self.station_id = station_id

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def min_height_by_launch(cls, id__):
        row = Reading.return_min_height(id__)
        return row

    @classmethod
    def get_launch_by_date(cls, date_time, station_id):
        row = db.session.query(cls).filter(cls.date == date_time).filter(cls.station_id == station_id).first()
        if row is None:
            return None
        return row.id

    @classmethod
    def get_launch_by_date_with_oni(cls, date_time, station_id, oni):
        row = db.session.query(cls).filter(cls.date == date_time).filter(cls.station_id == station_id).filter(cls.oni == oni).first()
        if row is None:
            return None
        return row.id

    @classmethod
    def get_readings_by_dates_no_oni(cls, begin_date, end_date, station_id):
        readings = []
        while begin_date != end_date:
            id_ = Launch.get_launch_by_date(begin_date, station_id)
            if id_ is None:
                new_reading = MonthlyAverages.get_average_by_date(begin_date, station_id)
                readings.append(new_reading)
                begin_date = begin_date + relativedelta(days=1)
            else:
                reading = Launch.min_height_by_launch(id_)
                if reading < 14000:
                    reading = MonthlyAverages.get_average_by_date(begin_date, station_id)
                readings.append(reading)
                begin_date = begin_date + relativedelta(days=1)
        return readings

    @classmethod
    def get_readings_by_date_with_oni(cls, dates_list, station_id, oni):
        readings = []
        for date in dates_list:
            id_ = Launch.get_launch_by_date_with_oni(date, station_id, oni)
            reading = Launch.min_height_by_launch(id_)
            readings.append(reading)
        return readings

    @classmethod
    def get_monthly_average(cls, missing_date, station_id):
        readings = []
        date = datetime(missing_date.year, missing_date.month, 1)
        end_date = date + relativedelta(days=+1, months=+1)
        print(date, end_date)
        print('Average called')
        while date != end_date:
            id_ = Launch.get_launch_by_date(date, station_id)
            if id_ is None:
                print('skip')
                date = date + relativedelta(days=+1)
            else:
                reading = Launch.min_height_by_launch(id_)
                readings.append(reading)
                print(reading)
                date = date + relativedelta(days=+1)
        new_date = datetime(missing_date.year, missing_date.month, 1)
        average = sum(readings) / len(readings)
        new_average = MonthlyAverages(new_date, average, station_id)
        new_average.save_to_db()
        print('average for {}/{} is {}'.format(missing_date.year, missing_date.month, average))
        return average

    @classmethod
    def get_oni_launch_dates(cls, begin_date, end_date, oni):
        dates = []
        while begin_date != end_date:
            row = db.session.query(cls).filter(cls.date == begin_date).filter(cls.oni == oni).first()
            if row is None:
                begin_date = begin_date + relativedelta(days=+1)
            else:
                dates.append(row.date)
                begin_date = begin_date + relativedelta(days=+1)
        return dates


class Reading(db.Model):

    __tablename__ = 'readings'

    id = db.Column(db.INTEGER, primary_key=True)
    height = db.Column(db.INTEGER)
    temp = db.Column(db.REAL)
    launch_id = db.Column(db.INTEGER, ForeignKey('launch.id'))
    launch = db.relationship('Launch')

    def __init__(self, height, temp, launch_id):
        self.height = height
        self.temp = temp
        self.launch_id = launch_id

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def return_min_height(cls, launch_id):
        rows = db.session.query(cls).filter(cls.launch_id == launch_id)
        height = 0
        temp = 0
        for row in rows:
            if row.temp < temp:
                temp = row.temp
                height = row.height

        return height


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


class MonthlyAverages(db.Model):
    __tablename__ = 'monthly'

    id = db.Column(db.INTEGER, primary_key=True)
    date = db.Column(db.DateTime)
    average = db.Column(db.REAL)
    station_id = db.Column(db.INTEGER, ForeignKey('stations.id'))
    parent = db.relationship("StationModel")

    def __init__(self, date, average, station_id):
        self.date = date
        self.average = average
        self.station_id = station_id

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_average_by_date(cls, date_time, station_id):
        date = date_time + relativedelta(day=1)
        row = db.session.query(cls).filter(cls.date == date).filter(cls.station_id == station_id).first()
        if row is None:
            reading = Launch.get_monthly_average(date, station_id)
            return reading
        else:
            return row.average


if __name__ == '__main__':
    from radiosonde.app import app
    db.init_app(app)
    db.create_all()

