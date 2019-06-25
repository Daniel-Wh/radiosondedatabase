from flask import Flask, render_template
from flask_restful import Api
from datetime import datetime
from models.station_model import Launch, StationModel, OniData
from dateutil.relativedelta import relativedelta
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


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/vis')
def bokeh_route():
    beg_date = datetime(2013, 1, 1, 0)
    end_date = datetime(2013, 1, 12, 0)
    readings = Launch.get_readings_by_dates_no_oni(beg_date, end_date, 1)
    s2readings = Launch.get_readings_by_dates_no_oni(beg_date, end_date, 2)
    dates = []
    x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    y = 0
    print(readings, s2readings)
    while beg_date != end_date:
        string_date = beg_date.strftime('%y%m%d')
        dates.append(string_date)
        beg_date = beg_date + relativedelta(days=+1)
        x.append(y)
        y += 1
    from bokeh.plotting import figure
    from bokeh.io import output_file, save
    from bokeh.models import ColumnDataSource
    output_file('templates\practice.html')
    f = figure()
    f.line(x, readings, color='red')
    f.line(x, s2readings, color='blue')
    save(f)
    return render_template('practice.html')


if __name__ == '__main__':

    app.run()
