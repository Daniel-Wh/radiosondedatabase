from flask import Flask
from flask_restful import Api
from models.station_model import StationData, StationModel
import sqlite3
from db import db


uri = 'sqlite:///data.db'
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = uri
api = Api(app)
db.init_app(app)


@app.before_first_request
def create_tables():
    db.create_all()
    from datetime import datetime
    from siphon.simplewebservice.igra2 import IGRAUpperAir
    from models.station_model import StationData, StationModel

    beginning = [datetime(2014, 9, 10, 0), datetime(2014, 9, 15, 0)]
    station = 'USM00072250'

    df, header = IGRAUpperAir.request_data(beginning, station)

    # date = header.date.dt.strftime('%Y%m%d').astype(str)
    # new_date = header['date'][0].dt.strftime('%Y%m%d').astype(int)
    new_date = ""
    x = 0
    while x < len(df['height']):
        date = df['date'][x].strftime("%y%m%d")
        if date != new_date:
            new_date = date
        new_station = StationData(new_date, 1, int(df['height'][x]), df['temperature'][x], 1)
        new_station.save_to_db()
        x += 1


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
