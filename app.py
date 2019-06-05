from flask import Flask
from flask_restful import Api
from models.station_model import StationData, StationModel, OniData
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
    y = OniData.find_by_date(2019, 1)
    print(y)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
