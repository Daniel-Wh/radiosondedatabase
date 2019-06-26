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
    station_2_readings = Launch.get_readings_by_dates_no_oni(datetime(2013, 1, 1, 12), datetime(2013, 12, 31, 12), 2)
    print(len(station_2_readings))



@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/vis')
def bokeh_route():
    begin_date = datetime(2013, 1, 1, 12)
    end_date = datetime(2013, 12, 31, 12)
    dates = []
    while begin_date != end_date:
        dates.append(begin_date)
        begin_date = begin_date + relativedelta(days=+1)

    station_1_readings = Launch.get_readings_by_dates_no_oni(datetime(2013, 1, 1, 12), datetime(2013, 12, 31, 12), 1)
    #station_2_readings = Launch.get_readings_by_dates_no_oni(datetime(2013, 1, 1, 12), datetime(2013, 12, 31, 12), 2)

    from bokeh.plotting import figure
    from bokeh.io import output_file, save
    from bokeh.models import ColumnDataSource

    chart_data = {
        'date': dates,
        'y1': station_1_readings
    }
    output_file('templates\practice.html')
    source = ColumnDataSource(chart_data)
    line = figure(plot_width=1200, plot_height=1000, x_axis_type='datetime')
    line.line(source=source, y='y1', x='date', color='blue')
    save(line)
    return render_template('practice.html')


if __name__ == '__main__':

    app.run()
